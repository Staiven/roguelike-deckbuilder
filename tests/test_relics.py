"""Tests for relic effects and event bus integration."""

import pytest
from src.entities.player import Player
from src.entities.enemy import Enemy, Intent, IntentType
from src.entities.card import CardInstance
from src.data.cards.starter_cards import STRIKE, DEFEND
from src.data.relics.common_relics import (
    create_relic_instance,
    BURNING_BLOOD,
    RING_OF_THE_SNAKE,
    ANCHOR,
    CENTENNIAL_PUZZLE,
    VAJRA,
)
from src.combat.combat_manager import CombatManager, CombatResult
from src.core.events import reset_event_bus


@pytest.fixture
def player():
    """Create a test player."""
    p = Player(name="Test", max_hp=50, current_hp=50)
    p.master_deck = [CardInstance(data=STRIKE) for _ in range(5)]
    return p


@pytest.fixture
def enemy():
    """Create a test enemy."""
    return Enemy(
        id="test_enemy",
        name="Test Enemy",
        max_hp=30,
        current_hp=30,
        intent=Intent(IntentType.ATTACK, damage=10),
    )


@pytest.fixture(autouse=True)
def reset_events():
    """Reset event bus before each test."""
    reset_event_bus()
    yield
    reset_event_bus()


class TestRelicEventSubscription:
    """Test that relics properly subscribe to events."""

    def test_burning_blood_heals_on_victory(self, player, enemy):
        """Burning Blood heals 6 HP at end of combat on victory."""
        relic = create_relic_instance("burning_blood")
        player.relics = [relic]
        player.current_hp = 30  # Start damaged

        manager = CombatManager()
        manager.start_combat(player, [enemy])

        # Kill the enemy
        enemy.current_hp = 0
        manager._check_combat_end()

        # Player should have been healed
        assert player.current_hp == 36  # 30 + 6 from Burning Blood

    def test_anchor_gives_block_at_combat_start(self, player, enemy):
        """Anchor gives 10 block at the start of combat."""
        relic = create_relic_instance("anchor")
        player.relics = [relic]

        manager = CombatManager()
        manager.start_combat(player, [enemy])

        assert player.block == 10

    def test_vajra_gives_strength_at_combat_start(self, player, enemy):
        """Vajra gives 1 Strength at the start of combat."""
        from src.core.enums import StatusEffectType

        relic = create_relic_instance("vajra")
        player.relics = [relic]

        manager = CombatManager()
        manager.start_combat(player, [enemy])

        assert player.status_effects.get(StatusEffectType.STRENGTH, 0) == 1

    def test_ring_of_snake_draws_extra_cards(self, player, enemy):
        """Ring of the Snake draws 2 extra cards at combat start."""
        relic = create_relic_instance("ring_of_the_snake")
        player.relics = [relic]
        # Add more cards so we can draw 7 (5 base + 2 from relic)
        player.master_deck.extend([CardInstance(data=DEFEND) for _ in range(5)])

        manager = CombatManager()
        manager.start_combat(player, [enemy])

        # Should have 7 cards (5 base draw + 2 from relic)
        assert len(manager.state.hand) == 7

    def test_centennial_puzzle_draws_on_first_damage(self, player, enemy):
        """Centennial Puzzle draws 3 cards on first HP loss."""
        relic = create_relic_instance("centennial_puzzle")
        player.relics = [relic]
        # Add more cards for draw
        player.master_deck.extend([CardInstance(data=DEFEND) for _ in range(10)])

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        initial_hand_size = len(state.hand)

        # Take damage
        player.take_damage(5)

        # Should have drawn 3 more cards
        assert len(state.hand) == initial_hand_size + 3

        # Taking more damage should not draw again
        player.take_damage(5)
        assert len(state.hand) == initial_hand_size + 3  # Still same

    def test_relics_unsubscribe_after_combat(self, player, enemy):
        """Relics should be unsubscribed from events after combat ends."""
        relic = create_relic_instance("anchor")
        player.relics = [relic]

        manager = CombatManager()
        manager.start_combat(player, [enemy])

        # Relic should have a subscription ID
        assert relic.event_subscription_id is not None

        # End combat
        enemy.current_hp = 0
        manager._check_combat_end()

        # Subscription should be cleared
        assert relic.event_subscription_id is None
