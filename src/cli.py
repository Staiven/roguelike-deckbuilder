"""Interactive CLI for the roguelike deck-builder game."""

from __future__ import annotations
import os
import sys
from typing import TYPE_CHECKING

from src.core.enums import MapNodeType
from src.core.events import reset_event_bus
from src.characters.base_character import Character, CharacterClass
from src.combat.combat_manager import CombatManager, CombatResult, CombatPhase
from src.map.map_generator import MapGenerator, GameMap
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
    from src.entities.card import CardInstance


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_divider() -> None:
    """Print a divider line."""
    print("-" * 60)


def get_input(prompt: str, valid_options: list[str] | None = None) -> str:
    """Get user input with optional validation."""
    while True:
        try:
            choice = input(prompt).strip().lower()
            if valid_options is None or choice in valid_options:
                return choice
            print(f"Invalid choice. Options: {', '.join(valid_options)}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            sys.exit(0)


def get_number_input(prompt: str, min_val: int, max_val: int) -> int:
    """Get a number input within a range."""
    while True:
        try:
            choice = input(prompt).strip()
            if choice.lower() == 'q':
                return -1  # Signal to quit/cancel
            num = int(choice)
            if min_val <= num <= max_val:
                return num
            print(f"Please enter a number between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a valid number (or 'q' to cancel)")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            sys.exit(0)


class InteractiveGame:
    """Interactive CLI game session."""

    def __init__(self) -> None:
        self.character: Character | None = None
        self.game_map: GameMap | None = None
        self.combat_manager: CombatManager = CombatManager()
        self.running = True
        self.floor = 0

    def run(self) -> None:
        """Main game loop."""
        clear_screen()
        self.show_title_screen()

        while self.running:
            if self.character is None:
                self.character_select()
            elif self.game_map is None:
                self.start_run()
            else:
                self.map_screen()

    def show_title_screen(self) -> None:
        """Display the title screen."""
        print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║      ██████╗  ██████╗  ██████╗ ██╗   ██╗███████╗          ║
    ║      ██╔══██╗██╔═══██╗██╔════╝ ██║   ██║██╔════╝          ║
    ║      ██████╔╝██║   ██║██║  ███╗██║   ██║█████╗            ║
    ║      ██╔══██╗██║   ██║██║   ██║██║   ██║██╔══╝            ║
    ║      ██║  ██║╚██████╔╝╚██████╔╝╚██████╔╝███████╗          ║
    ║      ╚═╝  ╚═╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝          ║
    ║                                                           ║
    ║              D E C K   B U I L D E R                      ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
        """)
        input("Press Enter to start...")

    def character_select(self) -> None:
        """Character selection screen."""
        clear_screen()
        print_header("SELECT YOUR CHARACTER")
        print()
        print("  [1] IRONCLAD - The Warrior")
        print("      HP: 80 | Energy: 3")
        print("      Relic: Burning Blood (Heal 6 HP after combat)")
        print("      A battle-hardened warrior with powerful attacks.")
        print()
        print("  [2] SILENT - The Huntress")
        print("      HP: 70 | Energy: 3")
        print("      Relic: Ring of the Snake (Draw 2 extra cards turn 1)")
        print("      A deadly huntress who uses poison and shivs.")
        print()
        print("  [q] Quit")
        print()

        choice = get_input("Choose your character: ", ["1", "2", "q"])

        if choice == "q":
            self.running = False
            return

        if choice == "1":
            self.character = Character.create(CharacterClass.WARRIOR)
            self.character.initialize_starting_deck(create_starter_deck_warrior())
            self.character.initialize_starting_relic(create_starter_relic_warrior())
        else:
            self.character = Character.create(CharacterClass.MAGE)
            self.character.initialize_starting_deck(create_starter_deck_mage())
            self.character.initialize_starting_relic(create_starter_relic_mage())

        print(f"\nYou selected {self.character.name}!")
        input("Press Enter to begin your run...")

    def start_run(self) -> None:
        """Initialize a new run."""
        reset_event_bus()
        generator = MapGenerator()
        self.game_map = generator.generate(act=1)
        self.floor = 0

    def map_screen(self) -> None:
        """Display the map and handle navigation."""
        if self.game_map is None or self.character is None:
            return

        clear_screen()
        print_header(f"ACT 1 - Floor {self.floor}")
        self.show_player_status()
        print_divider()
        print()
        print(self.game_map.render_ascii())
        print()
        print_divider()

        # Get available nodes
        available = self.game_map.get_available_nodes()

        if not available:
            # Check if we need to go to boss
            if self.game_map.boss_node and not self.game_map.boss_node.visited:
                print("\nThe path leads to the BOSS!")
                input("Press Enter to face the boss...")
                self.enter_node(self.game_map.boss_node)
                return
            else:
                print("\nYou have conquered Act 1!")
                input("Press Enter to continue...")
                self.running = False
                return

        print("\nAvailable paths:")
        for i, node in enumerate(available):
            node_desc = self.get_node_description(node.node_type)
            print(f"  [{i + 1}] {node.get_ascii_symbol()} - {node_desc}")

        print()
        print("  [d] View Deck")
        print("  [r] View Relics")
        print("  [q] Quit Run")
        print()

        # Get choice
        valid = [str(i + 1) for i in range(len(available))] + ["d", "r", "q"]
        choice = get_input("Choose your path: ", valid)

        if choice == "q":
            self.running = False
        elif choice == "d":
            self.view_deck()
        elif choice == "r":
            self.view_relics()
        else:
            node_idx = int(choice) - 1
            self.enter_node(available[node_idx])

    def get_node_description(self, node_type: MapNodeType) -> str:
        """Get a description for a node type."""
        descriptions = {
            MapNodeType.COMBAT: "Monster - Fight enemies",
            MapNodeType.ELITE: "Elite - Tough fight, better rewards",
            MapNodeType.REST: "Rest Site - Heal or upgrade",
            MapNodeType.SHOP: "Shop - Buy cards and relics",
            MapNodeType.EVENT: "Unknown - A mysterious encounter",
            MapNodeType.BOSS: "BOSS - The final challenge",
            MapNodeType.TREASURE: "Treasure - Free rewards",
        }
        return descriptions.get(node_type, "Unknown")

    def show_player_status(self) -> None:
        """Display player status bar."""
        if self.character is None:
            return
        p = self.character.player
        relic_str = ", ".join(r.name for r in p.relics) if p.relics else "None"
        print(f"  {self.character.name} | HP: {p.current_hp}/{p.max_hp} | "
              f"Gold: {p.gold} | Deck: {len(p.master_deck)} cards")

    def enter_node(self, node) -> None:
        """Enter a map node and handle the encounter."""
        if self.game_map is None:
            return

        self.game_map.move_to_node(node)
        self.floor += 1

        if node.node_type == MapNodeType.COMBAT:
            enemies = get_random_act1_encounter("normal")
            self.run_combat(enemies)
        elif node.node_type == MapNodeType.ELITE:
            enemies = get_random_act1_elite()
            self.run_combat(enemies, is_elite=True)
        elif node.node_type == MapNodeType.BOSS:
            enemies = get_act1_boss()
            self.run_combat(enemies, is_boss=True)
        elif node.node_type == MapNodeType.REST:
            self.rest_site()
        elif node.node_type == MapNodeType.SHOP:
            self.shop()
        elif node.node_type == MapNodeType.EVENT:
            self.event()
        elif node.node_type == MapNodeType.TREASURE:
            self.treasure()

    def run_combat(self, enemies: list[Enemy], is_elite: bool = False, is_boss: bool = False) -> None:
        """Run a combat encounter."""
        if self.character is None:
            return

        # Start combat
        state = self.combat_manager.start_combat(self.character.player, enemies)

        while state.result == CombatResult.IN_PROGRESS:
            clear_screen()

            # Header
            if is_boss:
                print_header("BOSS BATTLE")
            elif is_elite:
                print_header("ELITE COMBAT")
            else:
                print_header("COMBAT")

            # Show enemies
            print("\n  ENEMIES:")
            for i, enemy in enumerate(state.get_living_enemies()):
                intent_str = enemy.intent.get_display_string()
                status_str = ""
                if enemy.status_effects:
                    effects = [f"{k.name}:{v}" for k, v in enemy.status_effects.items()]
                    status_str = f" [{', '.join(effects)}]"
                print(f"    [{i + 1}] {enemy.name}: {enemy.current_hp}/{enemy.max_hp} HP "
                      f"| Block: {enemy.block} | Intent: {intent_str}{status_str}")

            print_divider()

            # Show player
            p = self.character.player
            status_str = ""
            if p.status_effects:
                effects = [f"{k.name}:{v}" for k, v in p.status_effects.items()]
                status_str = f" [{', '.join(effects)}]"
            print(f"\n  YOU: {p.current_hp}/{p.max_hp} HP | Block: {p.block} | "
                  f"Energy: {state.current_energy}/{state.energy_system.max_energy}{status_str}")

            print_divider()

            # Show hand
            print("\n  HAND:")
            for i, card in enumerate(state.hand):
                playable = "  " if state.energy_system.current_energy >= card.cost else "X "
                print(f"    {playable}[{i + 1}] {card.name} ({card.cost} energy) - {card.description}")

            print()
            print(f"  Draw: {len(state.draw_pile)} | Discard: {len(state.discard_pile)}")

            print_divider()
            print("\n  [#] Play card | [e] End turn | [d] View deck")
            print()

            choice = get_input("Action: ",
                [str(i + 1) for i in range(len(state.hand))] + ["e", "d"])

            if choice == "e":
                self.combat_manager.end_player_turn()
            elif choice == "d":
                self.view_deck()
                input("\nPress Enter to continue...")
            else:
                card_idx = int(choice) - 1
                card = state.hand[card_idx]

                # Check if card needs a target
                target = None
                living_enemies = state.get_living_enemies()

                if card.target_type.name == "SINGLE_ENEMY":
                    if len(living_enemies) == 1:
                        target = living_enemies[0]
                    else:
                        print("\nChoose target:")
                        for i, enemy in enumerate(living_enemies):
                            print(f"  [{i + 1}] {enemy.name} ({enemy.current_hp}/{enemy.max_hp})")
                        t_choice = get_number_input("Target: ", 1, len(living_enemies))
                        if t_choice == -1:
                            continue
                        target = living_enemies[t_choice - 1]

                can_play, reason = self.combat_manager.can_play_card(card, target)
                if can_play:
                    self.combat_manager.play_card(card, target)
                else:
                    print(f"\nCannot play: {reason}")
                    input("Press Enter to continue...")

        # Combat ended
        clear_screen()
        if state.result == CombatResult.VICTORY:
            print_header("VICTORY!")
            print(f"\n  You defeated the enemies!")
            print(f"  HP: {self.character.player.current_hp}/{self.character.player.max_hp}")

            # Burning Blood healing
            if self.character.player.has_relic("burning_blood"):
                healed = self.character.player.heal(6)
                if healed > 0:
                    print(f"  Burning Blood healed {healed} HP!")
                    print(f"  HP: {self.character.player.current_hp}/{self.character.player.max_hp}")

            # Gold reward
            gold = 15 if not is_elite else 30
            if is_boss:
                gold = 100
            self.character.player.gain_gold(gold)
            print(f"  Gained {gold} gold!")

            input("\nPress Enter to continue...")
        else:
            print_header("DEFEAT")
            print("\n  You have been slain...")
            print(f"  Reached floor {self.floor}")
            input("\nPress Enter to return to menu...")
            self.character = None
            self.game_map = None

    def rest_site(self) -> None:
        """Handle rest site interaction."""
        if self.character is None:
            return

        clear_screen()
        print_header("REST SITE")
        self.show_player_status()
        print()
        print("  The warm fire invites you to rest...")
        print()

        heal_amount = int(self.character.player.max_hp * 0.3)
        print(f"  [1] Rest - Heal {heal_amount} HP")
        print("  [2] Smith - Upgrade a card")
        print()

        choice = get_input("What do you do? ", ["1", "2"])

        if choice == "1":
            healed = self.character.player.heal(heal_amount)
            print(f"\n  You rest by the fire and recover {healed} HP.")
            print(f"  HP: {self.character.player.current_hp}/{self.character.player.max_hp}")
        else:
            self.upgrade_card()

        input("\nPress Enter to continue...")

    def upgrade_card(self) -> None:
        """Handle card upgrade."""
        if self.character is None:
            return

        upgradeable = [c for c in self.character.player.master_deck if c.can_upgrade()]

        if not upgradeable:
            print("\n  No cards available to upgrade!")
            return

        print("\n  Choose a card to upgrade:")
        for i, card in enumerate(upgradeable):
            print(f"    [{i + 1}] {card.name} -> {card.data.get_upgraded_name()}")

        choice = get_number_input("  Upgrade: ", 1, len(upgradeable))
        if choice == -1:
            return

        card = upgradeable[choice - 1]
        card.upgrade()
        print(f"\n  Upgraded {card.data.name} to {card.name}!")

    def shop(self) -> None:
        """Handle shop interaction."""
        clear_screen()
        print_header("SHOP")
        self.show_player_status()
        print()
        print("  The merchant greets you...")
        print()
        print("  (Shop not yet implemented)")
        input("\nPress Enter to continue...")

    def event(self) -> None:
        """Handle event interaction."""
        if self.character is None:
            return

        clear_screen()
        print_header("UNKNOWN EVENT")
        print()

        # Simple random event
        import random
        event_type = random.choice(["gold", "heal", "damage", "card"])

        if event_type == "gold":
            gold = random.randint(20, 50)
            print("  You find a hidden stash of gold!")
            self.character.player.gain_gold(gold)
            print(f"  Gained {gold} gold!")
        elif event_type == "heal":
            heal = random.randint(10, 20)
            healed = self.character.player.heal(heal)
            print("  You discover a healing spring!")
            print(f"  Healed {healed} HP!")
        elif event_type == "damage":
            damage = random.randint(5, 10)
            print("  You trigger a trap!")
            self.character.player.take_damage(damage, piercing=True)
            print(f"  Took {damage} damage!")
        else:
            print("  You find an ancient tome...")
            print("  (Card rewards not yet implemented)")

        input("\nPress Enter to continue...")

    def treasure(self) -> None:
        """Handle treasure room."""
        if self.character is None:
            return

        clear_screen()
        print_header("TREASURE")
        print()
        print("  You open the treasure chest...")
        print("  (Relic rewards not yet implemented)")

        # Give some gold for now
        gold = 50
        self.character.player.gain_gold(gold)
        print(f"  Found {gold} gold!")

        input("\nPress Enter to continue...")

    def view_deck(self) -> None:
        """Display the player's deck."""
        if self.character is None:
            return

        clear_screen()
        print_header("YOUR DECK")
        print()

        deck = sorted(self.character.player.master_deck,
                     key=lambda c: (c.card_type.value, c.name))

        for i, card in enumerate(deck):
            upgraded = "+" if card.upgraded else ""
            print(f"  {card.name}{upgraded} ({card.cost}) - {card.description}")

        print(f"\n  Total: {len(deck)} cards")

    def view_relics(self) -> None:
        """Display the player's relics."""
        if self.character is None:
            return

        clear_screen()
        print_header("YOUR RELICS")
        print()

        for relic in self.character.player.relics:
            print(f"  {relic.name}")
            print(f"    {relic.description}")
            print()

        if not self.character.player.relics:
            print("  No relics yet!")

        input("\nPress Enter to continue...")


def main() -> None:
    """Entry point for interactive CLI."""
    game = InteractiveGame()
    game.run()
    print("\nThanks for playing!")


if __name__ == "__main__":
    main()
