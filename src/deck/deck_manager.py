"""Deck management - draw, discard, shuffle logic."""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.core.events import get_event_bus, GameEvent, EventType

if TYPE_CHECKING:
    from src.entities.card import CardInstance


@dataclass
class DeckManager:
    """
    Manages the draw pile, hand, discard pile, and exhaust pile during combat.

    The master deck is owned by the Player; this class handles the combat-time
    card flow.
    """
    draw_pile: list[CardInstance] = field(default_factory=list)
    hand: list[CardInstance] = field(default_factory=list)
    discard_pile: list[CardInstance] = field(default_factory=list)
    exhaust_pile: list[CardInstance] = field(default_factory=list)
    max_hand_size: int = 10

    def initialize_from_deck(self, master_deck: list[CardInstance]) -> None:
        """
        Initialize the draw pile from the master deck at combat start.

        Creates copies of the cards so combat modifications don't affect
        the master deck.
        """
        self.draw_pile = [card.copy() for card in master_deck]
        self.hand = []
        self.discard_pile = []
        self.exhaust_pile = []
        self.shuffle_draw_pile()

    def shuffle_draw_pile(self) -> None:
        """Shuffle the draw pile."""
        random.shuffle(self.draw_pile)
        get_event_bus().emit(GameEvent.shuffle())

    def draw(self, count: int = 1) -> list[CardInstance]:
        """
        Draw cards from the draw pile into the hand.

        If the draw pile is empty, reshuffles the discard pile.
        Respects max hand size.

        Returns the cards that were actually drawn.
        """
        drawn: list[CardInstance] = []

        for _ in range(count):
            # Check hand size limit
            if len(self.hand) >= self.max_hand_size:
                break

            # Reshuffle if needed
            if not self.draw_pile:
                if not self.discard_pile:
                    break  # No cards left to draw
                self.reshuffle_discard_into_draw()

            if self.draw_pile:
                card = self.draw_pile.pop()
                self.hand.append(card)
                drawn.append(card)
                get_event_bus().emit(GameEvent.card_drawn(card))

        return drawn

    def reshuffle_discard_into_draw(self) -> None:
        """Move all cards from discard pile to draw pile and shuffle."""
        self.draw_pile.extend(self.discard_pile)
        self.discard_pile.clear()
        self.shuffle_draw_pile()

    def discard_card(self, card: CardInstance) -> bool:
        """
        Discard a card from the hand.

        Returns True if the card was in hand and discarded.
        """
        if card in self.hand:
            self.hand.remove(card)
            self.discard_pile.append(card)
            return True
        return False

    def discard_hand(self) -> list[CardInstance]:
        """
        Discard all cards in hand (except retained cards).

        Returns the cards that were discarded.
        """
        discarded: list[CardInstance] = []
        retained: list[CardInstance] = []

        for card in self.hand:
            if card.retain:
                retained.append(card)
            else:
                self.discard_pile.append(card)
                discarded.append(card)

        self.hand = retained
        return discarded

    def exhaust_card(self, card: CardInstance) -> bool:
        """
        Exhaust a card from the hand.

        Exhausted cards are removed from the combat entirely.
        Returns True if the card was in hand and exhausted.
        """
        if card in self.hand:
            self.hand.remove(card)
            self.exhaust_pile.append(card)
            get_event_bus().emit(GameEvent.card_exhausted(card))
            return True
        return False

    def exhaust_from_discard(self, card: CardInstance) -> bool:
        """Exhaust a card from the discard pile."""
        if card in self.discard_pile:
            self.discard_pile.remove(card)
            self.exhaust_pile.append(card)
            get_event_bus().emit(GameEvent.card_exhausted(card))
            return True
        return False

    def exhaust_from_draw(self, card: CardInstance) -> bool:
        """Exhaust a card from the draw pile."""
        if card in self.draw_pile:
            self.draw_pile.remove(card)
            self.exhaust_pile.append(card)
            get_event_bus().emit(GameEvent.card_exhausted(card))
            return True
        return False

    def add_card_to_hand(self, card: CardInstance) -> bool:
        """
        Add a card directly to hand (e.g., from a power effect).

        Returns True if added, False if hand is full.
        """
        if len(self.hand) >= self.max_hand_size:
            self.discard_pile.append(card)
            return False

        self.hand.append(card)
        return True

    def add_card_to_draw_pile(
        self,
        card: CardInstance,
        position: str = "random"
    ) -> None:
        """
        Add a card to the draw pile.

        Args:
            card: The card to add
            position: "top", "bottom", or "random"
        """
        if position == "top":
            self.draw_pile.append(card)
        elif position == "bottom":
            self.draw_pile.insert(0, card)
        else:  # random
            insert_pos = random.randint(0, len(self.draw_pile))
            self.draw_pile.insert(insert_pos, card)

    def add_card_to_discard(self, card: CardInstance) -> None:
        """Add a card to the discard pile."""
        self.discard_pile.append(card)

    def move_card_to_hand(self, card: CardInstance, from_pile: str) -> bool:
        """
        Move a card from a pile to the hand.

        Args:
            card: The card to move
            from_pile: "draw" or "discard"

        Returns True if successful.
        """
        if len(self.hand) >= self.max_hand_size:
            return False

        if from_pile == "draw" and card in self.draw_pile:
            self.draw_pile.remove(card)
            self.hand.append(card)
            return True
        elif from_pile == "discard" and card in self.discard_pile:
            self.discard_pile.remove(card)
            self.hand.append(card)
            return True

        return False

    def get_random_card_from_hand(self) -> CardInstance | None:
        """Get a random card from hand (for random discard effects)."""
        if not self.hand:
            return None
        return random.choice(self.hand)

    def clear_turn_modifiers(self) -> None:
        """Clear per-turn card modifiers at end of turn."""
        for card in self.hand + self.draw_pile + self.discard_pile:
            card.clear_turn_modifiers()

    def end_turn(self) -> list[CardInstance]:
        """
        Handle end of turn card management.

        - Discards non-retained cards
        - Exhausts ethereal cards
        - Clears turn modifiers

        Returns cards that were discarded.
        """
        exhausted: list[CardInstance] = []
        discarded: list[CardInstance] = []
        retained: list[CardInstance] = []

        for card in self.hand:
            if card.ethereal:
                self.exhaust_pile.append(card)
                exhausted.append(card)
                get_event_bus().emit(GameEvent.card_exhausted(card))
            elif card.retain:
                retained.append(card)
            else:
                self.discard_pile.append(card)
                discarded.append(card)

        self.hand = retained
        self.clear_turn_modifiers()

        return discarded

    def get_card_counts(self) -> dict[str, int]:
        """Get counts of cards in each pile."""
        return {
            "hand": len(self.hand),
            "draw": len(self.draw_pile),
            "discard": len(self.discard_pile),
            "exhaust": len(self.exhaust_pile),
        }

    def __str__(self) -> str:
        counts = self.get_card_counts()
        return (
            f"Hand: {counts['hand']}, "
            f"Draw: {counts['draw']}, "
            f"Discard: {counts['discard']}, "
            f"Exhaust: {counts['exhaust']}"
        )
