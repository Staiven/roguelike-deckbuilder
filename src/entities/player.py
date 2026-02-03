"""Player state management."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.core.enums import StatusEffectType
from src.core.events import get_event_bus, GameEvent

if TYPE_CHECKING:
    from src.entities.card import CardInstance
    from src.entities.relic import RelicInstance


@dataclass
class Player:
    """
    Represents the player's persistent state across the run.

    This includes health, gold, relics, and the master deck.
    Combat-specific state (hand, draw pile, etc.) is managed by CombatState.
    """
    name: str
    max_hp: int
    current_hp: int
    gold: int = 99
    max_energy: int = 3
    energy: int = 3
    block: int = 0
    master_deck: list[CardInstance] = field(default_factory=list)
    relics: list[RelicInstance] = field(default_factory=list)
    status_effects: dict[StatusEffectType, int] = field(default_factory=dict)
    potions: list = field(default_factory=list)
    max_potions: int = 3

    # Run statistics
    cards_played_this_combat: int = 0
    cards_played_this_turn: int = 0
    damage_dealt_this_combat: int = 0
    damage_taken_this_combat: int = 0

    # Combat runtime state (not persisted)
    _deck_manager: Any = field(default=None, repr=False)

    def is_alive(self) -> bool:
        """Check if the player is still alive."""
        return self.current_hp > 0

    def take_damage(self, amount: int, piercing: bool = False) -> int:
        """
        Deal damage to the player.

        Args:
            amount: Raw damage amount
            piercing: If True, ignores block

        Returns:
            Actual HP lost
        """
        if amount <= 0:
            return 0

        if piercing:
            blocked = 0
            remaining = amount
        else:
            blocked = min(self.block, amount)
            self.block -= blocked
            remaining = amount - blocked

        self.current_hp -= remaining
        self.current_hp = max(0, self.current_hp)
        self.damage_taken_this_combat += remaining

        # Emit HP_LOST event for relics like Centennial Puzzle
        if remaining > 0:
            event_bus = get_event_bus()
            event_bus.emit(GameEvent.hp_lost(self, remaining, self._deck_manager))

        return remaining

    def heal(self, amount: int) -> int:
        """
        Heal the player.

        Args:
            amount: Amount to heal

        Returns:
            Actual amount healed
        """
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp

    def gain_block(self, amount: int) -> int:
        """
        Gain block.

        Args:
            amount: Amount of block to gain

        Returns:
            Amount of block actually gained
        """
        if amount <= 0:
            return 0

        # Check for frail
        if self.status_effects.get(StatusEffectType.FRAIL, 0) > 0:
            amount = int(amount * 0.75)

        self.block += amount
        return amount

    def gain_max_hp(self, amount: int) -> None:
        """Increase max HP (also heals the same amount)."""
        self.max_hp += amount
        self.current_hp += amount

    def lose_max_hp(self, amount: int) -> None:
        """Decrease max HP."""
        self.max_hp = max(1, self.max_hp - amount)
        self.current_hp = min(self.current_hp, self.max_hp)

    def gain_gold(self, amount: int) -> None:
        """Gain gold."""
        self.gold += amount

    def spend_gold(self, amount: int) -> bool:
        """
        Spend gold.

        Returns True if successful, False if insufficient gold.
        """
        if self.gold < amount:
            return False
        self.gold -= amount
        return True

    def add_card_to_deck(self, card: CardInstance) -> None:
        """Add a card to the master deck."""
        self.master_deck.append(card)

    def remove_card_from_deck(self, card: CardInstance) -> bool:
        """Remove a card from the master deck."""
        if card in self.master_deck:
            self.master_deck.remove(card)
            return True
        return False

    def add_relic(self, relic: RelicInstance) -> None:
        """Add a relic to the player's collection."""
        self.relics.append(relic)

    def has_relic(self, relic_id: str) -> bool:
        """Check if player has a specific relic."""
        return any(r.data.id == relic_id for r in self.relics)

    def get_relic(self, relic_id: str) -> RelicInstance | None:
        """Get a specific relic by ID."""
        for relic in self.relics:
            if relic.data.id == relic_id:
                return relic
        return None

    def start_turn(self) -> None:
        """Called at the start of each turn."""
        self.energy = self.max_energy
        self.cards_played_this_turn = 0

    def end_turn(self) -> None:
        """Called at the end of each turn."""
        # Decrement status effect durations for turn-based effects
        for effect_type in [StatusEffectType.VULNERABLE, StatusEffectType.WEAK, StatusEffectType.FRAIL]:
            if effect_type in self.status_effects:
                self.status_effects[effect_type] -= 1
                if self.status_effects[effect_type] <= 0:
                    del self.status_effects[effect_type]

    def start_combat(self, deck_manager: Any = None) -> None:
        """Called at the start of combat."""
        self.block = 0
        self.status_effects.clear()
        self.cards_played_this_combat = 0
        self.damage_dealt_this_combat = 0
        self.damage_taken_this_combat = 0
        # Store deck_manager reference for relics that need to draw cards
        self._deck_manager = deck_manager

    def end_combat(self) -> None:
        """Called at the end of combat."""
        self.block = 0
        self.status_effects.clear()
        self._deck_manager = None

    def __str__(self) -> str:
        return f"{self.name} (HP: {self.current_hp}/{self.max_hp}, Gold: {self.gold})"
