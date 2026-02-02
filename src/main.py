"""Main entry point for the roguelike deck-builder game."""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

from src.core.enums import MapNodeType
from src.core.events import get_event_bus, reset_event_bus
from src.characters.base_character import Character, CharacterClass
from src.combat.combat_manager import CombatManager, CombatResult
from src.map.map_generator import MapGenerator, GameMap
from src.map.map_node import MapNode
from src.data.cards.starter_cards import create_starter_deck_warrior, create_starter_deck_mage
from src.data.enemies.act1_enemies import (
    get_random_act1_encounter,
    get_random_act1_elite,
    get_act1_boss,
)
from src.data.relics.common_relics import (
    create_starter_relic_warrior,
    create_starter_relic_mage,
)

if TYPE_CHECKING:
    from src.entities.player import Player
    from src.entities.enemy import Enemy


class GameState(Enum):
    """Overall game state."""
    MAIN_MENU = auto()
    MAP = auto()
    COMBAT = auto()
    EVENT = auto()
    SHOP = auto()
    REST = auto()
    REWARD = auto()
    GAME_OVER = auto()
    VICTORY = auto()


@dataclass
class GameSession:
    """
    Represents a single run of the game.

    Contains all the state needed for a complete playthrough.
    """
    character: Character
    current_map: GameMap | None = None
    state: GameState = GameState.MAIN_MENU
    combat_manager: CombatManager = field(default_factory=CombatManager)
    act: int = 1
    floor: int = 0
    ascension: int = 0
    seed: int | None = None

    def start_run(self) -> None:
        """Initialize a new run."""
        # Generate the first map
        generator = MapGenerator()
        self.current_map = generator.generate(act=self.act, seed=self.seed)
        self.state = GameState.MAP
        self.floor = 0

        # Reset event bus for fresh combat
        reset_event_bus()

    def can_move_to_node(self, node: MapNode) -> bool:
        """Check if the player can move to a node."""
        if self.current_map is None:
            return False
        return node in self.current_map.get_available_nodes()

    def move_to_node(self, node: MapNode) -> bool:
        """Move to a node and handle what happens there."""
        if not self.can_move_to_node(node):
            return False

        if self.current_map is None:
            return False

        self.current_map.move_to_node(node)
        self.floor += 1

        # Handle node type
        if node.node_type == MapNodeType.COMBAT:
            self._enter_combat(get_random_act1_encounter(ascension=self.ascension))
        elif node.node_type == MapNodeType.ELITE:
            self._enter_combat(get_random_act1_elite(ascension=self.ascension))
        elif node.node_type == MapNodeType.BOSS:
            self._enter_combat(get_act1_boss(ascension=self.ascension))
        elif node.node_type == MapNodeType.REST:
            self.state = GameState.REST
        elif node.node_type == MapNodeType.SHOP:
            self.state = GameState.SHOP
        elif node.node_type == MapNodeType.EVENT:
            self.state = GameState.EVENT
        elif node.node_type == MapNodeType.TREASURE:
            self.state = GameState.REWARD

        return True

    def _enter_combat(self, enemies: list[Enemy]) -> None:
        """Start a combat encounter."""
        self.state = GameState.COMBAT
        self.combat_manager.start_combat(
            player=self.character.player,
            enemies=enemies,
        )

    def end_combat(self, victory: bool) -> None:
        """Handle the end of combat."""
        self.character.player.end_combat()

        if victory:
            self.state = GameState.REWARD
        else:
            self.state = GameState.GAME_OVER

    def rest_heal(self) -> int:
        """Rest at a campfire to heal 30% of max HP."""
        heal_amount = int(self.character.player.max_hp * 0.3)
        actual_healed = self.character.player.heal(heal_amount)
        self.state = GameState.MAP
        return actual_healed

    def rest_upgrade(self) -> None:
        """Rest at a campfire to upgrade a card (would need card selection UI)."""
        # For now, just return to map
        self.state = GameState.MAP

    def collect_reward(self) -> None:
        """Collect rewards after combat/treasure."""
        # Would offer card rewards, gold, etc.
        self.state = GameState.MAP

    def is_run_complete(self) -> bool:
        """Check if the run is complete (all bosses defeated)."""
        if self.current_map is None:
            return False
        return self.current_map.is_complete()

    def get_status(self) -> dict:
        """Get a summary of the current game state."""
        player = self.character.player
        return {
            "character": self.character.name,
            "hp": f"{player.current_hp}/{player.max_hp}",
            "gold": player.gold,
            "deck_size": len(player.master_deck),
            "relics": len(player.relics),
            "act": self.act,
            "floor": self.floor,
            "state": self.state.name,
        }


def create_warrior_run(seed: int | None = None) -> GameSession:
    """Create a new game session with the Warrior character."""
    character = Character.create(CharacterClass.WARRIOR)
    character.initialize_starting_deck(create_starter_deck_warrior())
    character.initialize_starting_relic(create_starter_relic_warrior())

    return GameSession(character=character, seed=seed)


def create_mage_run(seed: int | None = None) -> GameSession:
    """Create a new game session with the Mage character."""
    character = Character.create(CharacterClass.MAGE)
    character.initialize_starting_deck(create_starter_deck_mage())
    character.initialize_starting_relic(create_starter_relic_mage())

    return GameSession(character=character, seed=seed)


def demo_combat() -> None:
    """Run a simple combat demo."""
    print("=" * 60)
    print("ROGUELIKE DECK-BUILDER - Combat Demo")
    print("=" * 60)

    # Create a warrior run
    session = create_warrior_run(seed=42)
    session.start_run()

    player = session.character.player
    print(f"\nPlayer: {player.name}")
    print(f"HP: {player.current_hp}/{player.max_hp}")
    print(f"Deck size: {len(player.master_deck)}")
    print(f"Starting relic: {player.relics[0].name}")

    # Start a combat
    enemies = get_random_act1_encounter("easy", ascension=0)
    session._enter_combat(enemies)

    combat = session.combat_manager
    state = combat.state

    print(f"\n--- Combat Start ---")
    print(f"Enemies: {[str(e) for e in enemies]}")

    # Play out a few turns
    turn_count = 0
    max_turns = 10

    while state.result == CombatResult.IN_PROGRESS and turn_count < max_turns:
        turn_count += 1
        print(f"\n=== Turn {turn_count} ===")

        # Show combat state
        summary = combat.get_combat_summary()
        print(f"Player HP: {summary['player_hp']}, Block: {summary['player_block']}")
        print(f"Energy: {summary['energy']}")
        print(f"Hand: {[str(c) for c in state.hand]}")
        print(f"Enemies: {summary['enemies']}")

        # Simple AI: play cards we can afford
        cards_played = 0
        for card in list(state.hand):
            can_play, _ = combat.can_play_card(card, enemies[0] if enemies[0].is_alive() else None)
            if can_play:
                target = None
                if card.target_type.name == "SINGLE_ENEMY":
                    # Find first living enemy
                    for e in state.get_living_enemies():
                        target = e
                        break

                result = combat.play_card(card, target)
                if result["success"]:
                    print(f"  Played: {card.name}")
                    cards_played += 1

        if cards_played == 0:
            print("  No playable cards")

        # End turn
        combat.end_player_turn()

        # Check if combat ended
        if state.result != CombatResult.IN_PROGRESS:
            break

    print(f"\n--- Combat End ---")
    print(f"Result: {state.result.name}")
    print(f"Player HP: {player.current_hp}/{player.max_hp}")


def demo_map() -> None:
    """Run a map generation demo."""
    print("=" * 60)
    print("ROGUELIKE DECK-BUILDER - Map Demo")
    print("=" * 60)

    generator = MapGenerator()
    game_map = generator.generate(act=1, seed=42)

    print("\nGenerated Map:")
    print(game_map.render_ascii())

    print("\nAvailable starting nodes:")
    for node in game_map.get_available_nodes():
        print(f"  {node}")


def main() -> None:
    """Main entry point."""
    print("Welcome to the Roguelike Deck-Builder!")
    print("\nRunning demos...\n")

    demo_map()
    print("\n")
    demo_combat()

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
