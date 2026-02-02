"""Tests for deck management."""

import pytest
from src.core.events import reset_event_bus
from src.deck.deck_manager import DeckManager
from src.entities.card import CardData, CardInstance
from src.core.enums import CardType, CardRarity, TargetType
from src.core.effects import DamageEffect


@pytest.fixture(autouse=True)
def reset_events():
    """Reset event bus before each test."""
    reset_event_bus()


@pytest.fixture
def sample_card() -> CardData:
    """Create a sample card for testing."""
    return CardData(
        id="test_strike",
        name="Test Strike",
        card_type=CardType.ATTACK,
        rarity=CardRarity.STARTER,
        target_type=TargetType.SINGLE_ENEMY,
        base_cost=1,
        base_effects=[DamageEffect(base_damage=6)],
        description="Deal 6 damage.",
    )


@pytest.fixture
def deck_manager(sample_card: CardData) -> DeckManager:
    """Create a deck manager with a 10-card deck."""
    cards = [CardInstance(data=sample_card) for _ in range(10)]
    manager = DeckManager()
    manager.initialize_from_deck(cards)
    return manager


class TestDeckManager:
    def test_initialize_from_deck(self, sample_card: CardData):
        """Test initializing deck manager from master deck."""
        cards = [CardInstance(data=sample_card) for _ in range(10)]
        manager = DeckManager()
        manager.initialize_from_deck(cards)

        assert len(manager.draw_pile) == 10
        assert len(manager.hand) == 0
        assert len(manager.discard_pile) == 0
        assert len(manager.exhaust_pile) == 0

    def test_draw_cards(self, deck_manager: DeckManager):
        """Test drawing cards from draw pile to hand."""
        drawn = deck_manager.draw(5)

        assert len(drawn) == 5
        assert len(deck_manager.hand) == 5
        assert len(deck_manager.draw_pile) == 5

    def test_draw_respects_hand_size(self, deck_manager: DeckManager):
        """Test that drawing respects max hand size."""
        deck_manager.max_hand_size = 5
        drawn = deck_manager.draw(10)

        assert len(drawn) == 5
        assert len(deck_manager.hand) == 5

    def test_discard_card(self, deck_manager: DeckManager):
        """Test discarding a card from hand."""
        deck_manager.draw(3)
        initial_hand_size = len(deck_manager.hand)
        card = deck_manager.hand[0]

        result = deck_manager.discard_card(card)

        assert result is True
        # Check size changed correctly (all cards look the same, so check sizes)
        assert len(deck_manager.hand) == initial_hand_size - 1
        assert len(deck_manager.discard_pile) == 1

    def test_discard_hand(self, deck_manager: DeckManager):
        """Test discarding entire hand."""
        deck_manager.draw(5)
        discarded = deck_manager.discard_hand()

        assert len(discarded) == 5
        assert len(deck_manager.hand) == 0
        assert len(deck_manager.discard_pile) == 5

    def test_exhaust_card(self, deck_manager: DeckManager):
        """Test exhausting a card."""
        deck_manager.draw(3)
        initial_hand_size = len(deck_manager.hand)
        card = deck_manager.hand[0]

        result = deck_manager.exhaust_card(card)

        assert result is True
        # Check size changed correctly
        assert len(deck_manager.hand) == initial_hand_size - 1
        assert len(deck_manager.exhaust_pile) == 1

    def test_reshuffle_discard(self, deck_manager: DeckManager):
        """Test reshuffling discard pile into draw pile."""
        # Draw all cards
        deck_manager.draw(10)
        assert len(deck_manager.draw_pile) == 0
        assert len(deck_manager.hand) == 10

        # Discard all
        deck_manager.discard_hand()
        assert len(deck_manager.discard_pile) == 10

        # Drawing should trigger reshuffle
        drawn = deck_manager.draw(5)

        assert len(drawn) == 5
        assert len(deck_manager.hand) == 5
        assert len(deck_manager.draw_pile) == 5
        assert len(deck_manager.discard_pile) == 0

    def test_get_card_counts(self, deck_manager: DeckManager):
        """Test getting card counts from all piles."""
        deck_manager.draw(3)
        deck_manager.discard_card(deck_manager.hand[0])
        deck_manager.exhaust_card(deck_manager.hand[0])

        counts = deck_manager.get_card_counts()

        assert counts["hand"] == 1
        assert counts["draw"] == 7
        assert counts["discard"] == 1
        assert counts["exhaust"] == 1
