"""Event bus for game events - allows relics and effects to react to game state changes."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from src.entities.card import CardInstance
    from src.entities.player import Player
    from src.entities.enemy import Enemy


class EventType(Enum):
    """Types of events that can occur in the game."""
    # Combat events
    COMBAT_START = auto()
    COMBAT_END = auto()
    TURN_START = auto()
    TURN_END = auto()
    ENEMY_TURN_START = auto()
    ENEMY_TURN_END = auto()

    # Card events
    CARD_DRAWN = auto()
    CARD_PLAYED = auto()
    CARD_EXHAUSTED = auto()
    CARD_DISCARDED = auto()

    # Damage events
    DAMAGE_DEALT = auto()
    DAMAGE_TAKEN = auto()
    BLOCK_GAINED = auto()
    BLOCK_LOST = auto()

    # Health events
    HP_LOST = auto()
    HP_GAINED = auto()
    ENEMY_DIED = auto()

    # Status events
    STATUS_APPLIED = auto()
    STATUS_REMOVED = auto()

    # Energy events
    ENERGY_GAINED = auto()
    ENERGY_SPENT = auto()

    # Deck events
    SHUFFLE = auto()

    # Map events
    ROOM_ENTERED = auto()
    REST_SITE_USED = auto()

    # Relic events
    RELIC_OBTAINED = auto()

    # Gold events
    GOLD_GAINED = auto()
    GOLD_SPENT = auto()


@dataclass
class GameEvent:
    """A game event with associated data."""
    event_type: EventType
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def combat_start(cls, player: Player, enemies: list[Enemy]) -> GameEvent:
        return cls(EventType.COMBAT_START, {"player": player, "enemies": enemies})

    @classmethod
    def combat_end(cls, victory: bool) -> GameEvent:
        return cls(EventType.COMBAT_END, {"victory": victory})

    @classmethod
    def turn_start(cls, turn_number: int) -> GameEvent:
        return cls(EventType.TURN_START, {"turn_number": turn_number})

    @classmethod
    def turn_end(cls, turn_number: int) -> GameEvent:
        return cls(EventType.TURN_END, {"turn_number": turn_number})

    @classmethod
    def card_played(cls, card: CardInstance, target: Any = None) -> GameEvent:
        return cls(EventType.CARD_PLAYED, {"card": card, "target": target})

    @classmethod
    def card_drawn(cls, card: CardInstance) -> GameEvent:
        return cls(EventType.CARD_DRAWN, {"card": card})

    @classmethod
    def card_exhausted(cls, card: CardInstance) -> GameEvent:
        return cls(EventType.CARD_EXHAUSTED, {"card": card})

    @classmethod
    def damage_dealt(cls, source: Any, target: Any, amount: int) -> GameEvent:
        return cls(EventType.DAMAGE_DEALT, {
            "source": source,
            "target": target,
            "amount": amount,
        })

    @classmethod
    def enemy_died(cls, enemy: Enemy) -> GameEvent:
        return cls(EventType.ENEMY_DIED, {"enemy": enemy})

    @classmethod
    def hp_lost(cls, entity: Any, amount: int) -> GameEvent:
        return cls(EventType.HP_LOST, {"entity": entity, "amount": amount})

    @classmethod
    def shuffle(cls) -> GameEvent:
        return cls(EventType.SHUFFLE, {})


# Type alias for event handlers
EventHandler = Callable[[GameEvent], None]


class EventBus:
    """
    Central event bus for the game.

    Allows relics, powers, and other game elements to subscribe to
    and react to game events.
    """

    def __init__(self) -> None:
        self._handlers: dict[EventType, list[tuple[int, EventHandler]]] = {}
        self._handler_ids: dict[int, tuple[EventType, EventHandler]] = {}
        self._next_id = 0

    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler,
        priority: int = 0,
    ) -> int:
        """
        Subscribe to an event type.

        Args:
            event_type: The type of event to listen for
            handler: Function to call when event occurs
            priority: Higher priority handlers run first (default 0)

        Returns:
            A subscription ID that can be used to unsubscribe
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        handler_id = self._next_id
        self._next_id += 1

        self._handlers[event_type].append((priority, handler))
        self._handlers[event_type].sort(key=lambda x: -x[0])  # Higher priority first

        self._handler_ids[handler_id] = (event_type, handler)

        return handler_id

    def unsubscribe(self, handler_id: int) -> bool:
        """
        Unsubscribe from an event.

        Args:
            handler_id: The ID returned from subscribe()

        Returns:
            True if successfully unsubscribed, False if ID not found
        """
        if handler_id not in self._handler_ids:
            return False

        event_type, handler = self._handler_ids[handler_id]

        self._handlers[event_type] = [
            (p, h) for p, h in self._handlers[event_type] if h != handler
        ]

        del self._handler_ids[handler_id]
        return True

    def emit(self, event: GameEvent) -> None:
        """
        Emit an event to all subscribers.

        Args:
            event: The event to emit
        """
        if event.event_type not in self._handlers:
            return

        for _, handler in self._handlers[event.event_type]:
            handler(event)

    def clear(self) -> None:
        """Clear all event subscriptions."""
        self._handlers.clear()
        self._handler_ids.clear()
        self._next_id = 0


# Global event bus instance
_global_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (useful for testing)."""
    global _global_event_bus
    if _global_event_bus:
        _global_event_bus.clear()
    _global_event_bus = EventBus()
