"""Relic data model - passive items that provide bonuses."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable, Any

from src.core.enums import RelicRarity
from src.core.events import EventType, GameEvent, EventHandler

if TYPE_CHECKING:
    from src.entities.player import Player


class RelicTrigger(Enum):
    """When a relic's effect activates."""
    PASSIVE = auto()           # Always active
    ON_PICKUP = auto()         # When first obtained
    COMBAT_START = auto()      # At the start of each combat
    COMBAT_END = auto()        # At the end of each combat
    TURN_START = auto()        # At the start of each turn
    TURN_END = auto()          # At the end of each turn
    ON_CARD_PLAY = auto()      # When a card is played
    ON_ATTACK = auto()         # When an attack card is played
    ON_SKILL = auto()          # When a skill card is played
    ON_POWER = auto()          # When a power card is played
    ON_DAMAGE_DEALT = auto()   # When damage is dealt
    ON_DAMAGE_TAKEN = auto()   # When damage is taken
    ON_BLOCK = auto()          # When block is gained
    ON_HP_LOSS = auto()        # When HP is lost
    ON_HEAL = auto()           # When healed
    ON_GOLD_GAIN = auto()      # When gold is gained
    ON_CHEST_OPEN = auto()     # When opening a chest
    ON_REST = auto()           # When resting at a campfire
    ON_SHUFFLE = auto()        # When draw pile is shuffled
    ON_EXHAUST = auto()        # When a card is exhausted


# Type for relic effect functions
RelicEffect = Callable[["RelicInstance", GameEvent, "Player"], Any]


@dataclass
class RelicData:
    """
    Immutable relic definition.

    This represents the base template for a relic.
    """
    id: str
    name: str
    rarity: RelicRarity
    description: str
    trigger: RelicTrigger
    effect: RelicEffect | None = None
    counter_based: bool = False
    max_counter: int | None = None

    def get_event_type(self) -> EventType | None:
        """Map relic trigger to event type for subscription."""
        mapping = {
            RelicTrigger.COMBAT_START: EventType.COMBAT_START,
            RelicTrigger.COMBAT_END: EventType.COMBAT_END,
            RelicTrigger.TURN_START: EventType.TURN_START,
            RelicTrigger.TURN_END: EventType.TURN_END,
            RelicTrigger.ON_CARD_PLAY: EventType.CARD_PLAYED,
            RelicTrigger.ON_DAMAGE_DEALT: EventType.DAMAGE_DEALT,
            RelicTrigger.ON_DAMAGE_TAKEN: EventType.DAMAGE_TAKEN,
            RelicTrigger.ON_HP_LOSS: EventType.HP_LOST,
            RelicTrigger.ON_SHUFFLE: EventType.SHUFFLE,
            RelicTrigger.ON_EXHAUST: EventType.CARD_EXHAUSTED,
        }
        return mapping.get(self.trigger)


@dataclass
class RelicInstance:
    """
    A specific instance of a relic owned by the player.

    Wraps RelicData with runtime state like counters and
    whether the relic is currently active.
    """
    data: RelicData
    counter: int = 0
    enabled: bool = True
    event_subscription_id: int | None = None

    @property
    def id(self) -> str:
        return self.data.id

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def rarity(self) -> RelicRarity:
        return self.data.rarity

    @property
    def description(self) -> str:
        desc = self.data.description
        if self.data.counter_based:
            desc = desc.replace("{counter}", str(self.counter))
        return desc

    @property
    def trigger(self) -> RelicTrigger:
        return self.data.trigger

    def increment_counter(self, amount: int = 1) -> int:
        """Increment the counter, respecting max if set."""
        self.counter += amount
        if self.data.max_counter is not None:
            self.counter = min(self.counter, self.data.max_counter)
        return self.counter

    def reset_counter(self) -> None:
        """Reset the counter to zero."""
        self.counter = 0

    def activate(self, event: GameEvent, player: Player) -> Any:
        """
        Activate this relic's effect.

        Args:
            event: The triggering event
            player: The player who owns this relic

        Returns:
            Result of the effect, if any
        """
        if not self.enabled or self.data.effect is None:
            return None

        return self.data.effect(self, event, player)

    def create_event_handler(self, player: Player) -> EventHandler:
        """Create an event handler for this relic."""
        def handler(event: GameEvent) -> None:
            self.activate(event, player)
        return handler

    def disable(self) -> None:
        """Disable this relic (some relics can be turned off)."""
        self.enabled = False

    def enable(self) -> None:
        """Enable this relic."""
        self.enabled = True

    def __str__(self) -> str:
        counter_str = f" ({self.counter})" if self.data.counter_based else ""
        return f"{self.name}{counter_str}"

    def __repr__(self) -> str:
        return f"RelicInstance({self.name}, counter={self.counter}, enabled={self.enabled})"
