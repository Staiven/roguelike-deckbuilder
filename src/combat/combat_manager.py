"""Combat orchestration - turn-based combat management."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from src.core.enums import CardType, TargetType
from src.core.events import get_event_bus, GameEvent, EventType
from src.deck.deck_manager import DeckManager
from src.combat.energy_system import EnergySystem
from src.combat.status_effects import process_end_of_turn_effects

if TYPE_CHECKING:
    from src.entities.card import CardInstance
    from src.entities.player import Player
    from src.entities.enemy import Enemy


class CombatResult(Enum):
    """Possible outcomes of combat."""
    IN_PROGRESS = auto()
    VICTORY = auto()
    DEFEAT = auto()


class CombatPhase(Enum):
    """Current phase of combat."""
    NOT_STARTED = auto()
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    COMBAT_END = auto()


@dataclass
class CombatState:
    """
    Complete state of an ongoing combat encounter.

    This is the main object passed to effects and used for combat logic.
    """
    player: Player
    enemies: list[Enemy]
    deck_manager: DeckManager = field(default_factory=DeckManager)
    energy_system: EnergySystem = field(default_factory=EnergySystem)
    turn_number: int = 0
    phase: CombatPhase = CombatPhase.NOT_STARTED
    result: CombatResult = CombatResult.IN_PROGRESS

    @property
    def draw_pile(self) -> list[CardInstance]:
        return self.deck_manager.draw_pile

    @property
    def hand(self) -> list[CardInstance]:
        return self.deck_manager.hand

    @property
    def discard_pile(self) -> list[CardInstance]:
        return self.deck_manager.discard_pile

    @property
    def exhaust_pile(self) -> list[CardInstance]:
        return self.deck_manager.exhaust_pile

    @property
    def current_energy(self) -> int:
        return self.energy_system.current_energy

    def get_living_enemies(self) -> list[Enemy]:
        """Get all enemies that are still alive."""
        return [e for e in self.enemies if e.is_alive()]


class CombatManager:
    """
    Manages the flow of a combat encounter.

    Handles turn phases, card playing, and combat resolution.
    """

    def __init__(self) -> None:
        self.state: CombatState | None = None
        self.event_bus = get_event_bus()

    def start_combat(
        self,
        player: Player,
        enemies: list[Enemy],
        draw_count: int = 5
    ) -> CombatState:
        """
        Initialize a new combat encounter.

        Args:
            player: The player in combat
            enemies: List of enemies to fight
            draw_count: Number of cards to draw at start of turn

        Returns:
            The combat state
        """
        self.state = CombatState(player=player, enemies=enemies)
        self.draw_count = draw_count

        # Initialize combat state
        player.start_combat()
        self.state.deck_manager.initialize_from_deck(player.master_deck)
        self.state.energy_system.initialize(player)

        # Emit combat start event
        self.event_bus.emit(GameEvent.combat_start(player, enemies))

        # Set up enemy intents
        for enemy in enemies:
            enemy.choose_intent(self.state)

        # Start first turn
        self._start_player_turn()

        return self.state

    def _start_player_turn(self) -> None:
        """Begin the player's turn."""
        if self.state is None:
            return

        self.state.turn_number += 1
        self.state.phase = CombatPhase.PLAYER_TURN

        # Reset block (unless player has artifact/power that says otherwise)
        self.state.player.block = 0

        # Refresh energy
        self.state.energy_system.start_turn()
        self.state.player.energy = self.state.energy_system.current_energy

        # Draw cards
        self.state.deck_manager.draw(self.draw_count)

        # Emit turn start event
        self.event_bus.emit(GameEvent.turn_start(self.state.turn_number))

        # Reset player turn counter
        self.state.player.cards_played_this_turn = 0

    def can_play_card(self, card: CardInstance, target: Enemy | None = None) -> tuple[bool, str]:
        """
        Check if a card can be played.

        Returns (can_play, reason).
        """
        if self.state is None:
            return False, "No active combat"

        if self.state.phase != CombatPhase.PLAYER_TURN:
            return False, "Not player's turn"

        if card not in self.state.hand:
            return False, "Card not in hand"

        if card.unplayable:
            return False, "Card is unplayable"

        # Check energy
        if self.state.energy_system.current_energy < card.cost:
            return False, "Not enough energy"

        # Check targeting
        if card.target_type == TargetType.SINGLE_ENEMY:
            if target is None:
                return False, "Must select a target"
            if target not in self.state.get_living_enemies():
                return False, "Invalid target"

        return True, ""

    def play_card(
        self,
        card: CardInstance,
        target: Enemy | None = None
    ) -> dict[str, Any]:
        """
        Play a card from hand.

        Args:
            card: The card to play
            target: Target enemy (if required)

        Returns:
            Dict with results of playing the card
        """
        if self.state is None:
            return {"success": False, "reason": "No active combat"}

        can_play, reason = self.can_play_card(card, target)
        if not can_play:
            return {"success": False, "reason": reason}

        results: dict[str, Any] = {
            "success": True,
            "card": card,
            "effects": [],
        }

        # Spend energy
        self.state.energy_system.spend(card.cost)
        self.state.player.energy = self.state.energy_system.current_energy

        # Remove from hand
        self.state.hand.remove(card)

        # Determine targets for effects
        effect_target: Any = None
        if card.target_type == TargetType.SINGLE_ENEMY:
            effect_target = target
        elif card.target_type == TargetType.ALL_ENEMIES:
            effect_target = self.state.get_living_enemies()
        elif card.target_type == TargetType.SELF:
            effect_target = self.state.player

        # Apply effects
        for effect in card.effects:
            effect_result = effect.apply(
                self.state,
                self.state.player,
                effect_target
            )
            results["effects"].append(effect_result)

        # Emit card played event
        self.event_bus.emit(GameEvent.card_played(card, target))

        # Handle card destination
        if card.exhaust:
            self.state.exhaust_pile.append(card)
        else:
            self.state.discard_pile.append(card)

        # Update counters
        self.state.player.cards_played_this_turn += 1
        self.state.player.cards_played_this_combat += 1

        # Check for enemy deaths
        self._check_enemy_deaths()

        # Check for combat end
        self._check_combat_end()

        return results

    def end_player_turn(self) -> dict[str, Any]:
        """
        End the player's turn and begin enemy turn.

        Returns information about what happened.
        """
        if self.state is None:
            return {"success": False, "reason": "No active combat"}

        if self.state.phase != CombatPhase.PLAYER_TURN:
            return {"success": False, "reason": "Not player's turn"}

        results: dict[str, Any] = {"success": True}

        # Emit turn end event
        self.event_bus.emit(GameEvent.turn_end(self.state.turn_number))

        # Discard hand / handle end of turn effects
        discarded = self.state.deck_manager.end_turn()
        results["discarded"] = discarded

        # Process player end of turn status effects
        status_results = process_end_of_turn_effects(self.state.player)
        results["status_effects"] = status_results

        # Unspent energy
        self.state.energy_system.end_turn()

        # Begin enemy turn
        self._execute_enemy_turn()

        return results

    def _execute_enemy_turn(self) -> dict[str, Any]:
        """Execute all enemy actions."""
        if self.state is None:
            return {}

        self.state.phase = CombatPhase.ENEMY_TURN
        results: dict[str, Any] = {"enemy_actions": []}

        for enemy in self.state.get_living_enemies():
            # Start enemy turn (clears block)
            enemy.start_turn()

            # Execute intent
            action_result = enemy.execute_intent(self.state)
            results["enemy_actions"].append({
                "enemy": enemy,
                "result": action_result,
            })

            # Check if player died
            if not self.state.player.is_alive():
                self.state.result = CombatResult.DEFEAT
                self.state.phase = CombatPhase.COMBAT_END
                self.event_bus.emit(GameEvent.combat_end(victory=False))
                return results

            # End enemy turn (process poison, etc.)
            enemy.end_turn()

            # Check if enemy died from poison
            if not enemy.is_alive():
                self.event_bus.emit(GameEvent.enemy_died(enemy))

        # Check combat end
        self._check_combat_end()

        if self.state.result == CombatResult.IN_PROGRESS:
            # Choose new intents for next turn
            for enemy in self.state.get_living_enemies():
                enemy.choose_intent(self.state)

            # Start next player turn
            self._start_player_turn()

        return results

    def _check_enemy_deaths(self) -> None:
        """Check for and handle enemy deaths."""
        if self.state is None:
            return

        for enemy in self.state.enemies:
            if not enemy.is_alive():
                self.event_bus.emit(GameEvent.enemy_died(enemy))

    def _check_combat_end(self) -> None:
        """Check if combat should end."""
        if self.state is None:
            return

        # Check for victory
        if not self.state.get_living_enemies():
            self.state.result = CombatResult.VICTORY
            self.state.phase = CombatPhase.COMBAT_END
            self.event_bus.emit(GameEvent.combat_end(victory=True))
            return

        # Check for defeat
        if not self.state.player.is_alive():
            self.state.result = CombatResult.DEFEAT
            self.state.phase = CombatPhase.COMBAT_END
            self.event_bus.emit(GameEvent.combat_end(victory=False))

    def get_combat_summary(self) -> dict[str, Any]:
        """Get a summary of the current combat state."""
        if self.state is None:
            return {"active": False}

        return {
            "active": True,
            "turn": self.state.turn_number,
            "phase": self.state.phase.name,
            "result": self.state.result.name,
            "player_hp": f"{self.state.player.current_hp}/{self.state.player.max_hp}",
            "player_block": self.state.player.block,
            "energy": f"{self.state.current_energy}/{self.state.energy_system.max_energy}",
            "hand_size": len(self.state.hand),
            "draw_pile": len(self.state.draw_pile),
            "discard_pile": len(self.state.discard_pile),
            "enemies": [
                {
                    "name": e.name,
                    "hp": f"{e.current_hp}/{e.max_hp}",
                    "block": e.block,
                    "intent": e.intent.get_display_string(),
                }
                for e in self.state.get_living_enemies()
            ],
        }
