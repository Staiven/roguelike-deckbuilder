"""Card data model - the primary game object."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.core.enums import CardType, CardRarity, TargetType

if TYPE_CHECKING:
    from src.core.effects import Effect


@dataclass
class CardData:
    """
    Immutable card definition.

    This represents the base template for a card. CardInstance wraps this
    with runtime modifications (cost changes, upgrades, etc.).
    """
    id: str
    name: str
    card_type: CardType
    rarity: CardRarity
    target_type: TargetType
    base_cost: int
    base_effects: list[Effect]
    description: str
    upgraded_name: str | None = None
    upgraded_cost: int | None = None
    upgraded_effects: list[Effect] | None = None
    upgraded_description: str | None = None
    exhaust: bool = False
    ethereal: bool = False
    innate: bool = False
    retain: bool = False
    unplayable: bool = False

    def get_upgraded_name(self) -> str:
        """Get the name when upgraded."""
        if self.upgraded_name:
            return self.upgraded_name
        return f"{self.name}+"


@dataclass
class CardInstance:
    """
    A specific instance of a card in play.

    Wraps CardData with runtime state like whether it's upgraded,
    temporary cost modifications, etc.
    """
    data: CardData
    upgraded: bool = False
    cost_modifier: int = 0
    cost_this_turn: int | None = None
    cost_this_combat: int | None = None

    @property
    def id(self) -> str:
        return self.data.id

    @property
    def name(self) -> str:
        if self.upgraded:
            return self.data.get_upgraded_name()
        return self.data.name

    @property
    def card_type(self) -> CardType:
        return self.data.card_type

    @property
    def rarity(self) -> CardRarity:
        return self.data.rarity

    @property
    def target_type(self) -> TargetType:
        return self.data.target_type

    @property
    def cost(self) -> int:
        """Get the current cost of this card."""
        # Check for temporary cost overrides
        if self.cost_this_turn is not None:
            return max(0, self.cost_this_turn)
        if self.cost_this_combat is not None:
            return max(0, self.cost_this_combat)

        # Base cost (possibly upgraded) plus modifiers
        base = self.data.base_cost
        if self.upgraded and self.data.upgraded_cost is not None:
            base = self.data.upgraded_cost

        return max(0, base + self.cost_modifier)

    @property
    def effects(self) -> list[Effect]:
        """Get the current effects of this card."""
        if self.upgraded and self.data.upgraded_effects is not None:
            return self.data.upgraded_effects
        return self.data.base_effects

    @property
    def description(self) -> str:
        """Get the current description of this card."""
        if self.upgraded and self.data.upgraded_description is not None:
            return self.data.upgraded_description
        return self.data.description

    @property
    def exhaust(self) -> bool:
        return self.data.exhaust

    @property
    def ethereal(self) -> bool:
        return self.data.ethereal

    @property
    def innate(self) -> bool:
        return self.data.innate

    @property
    def retain(self) -> bool:
        return self.data.retain

    @property
    def unplayable(self) -> bool:
        return self.data.unplayable

    def can_upgrade(self) -> bool:
        """Check if this card can be upgraded."""
        return not self.upgraded

    def upgrade(self) -> bool:
        """
        Upgrade this card instance.

        Returns True if successfully upgraded, False if already upgraded.
        """
        if self.upgraded:
            return False
        self.upgraded = True
        return True

    def set_cost_this_turn(self, cost: int) -> None:
        """Set a temporary cost for this turn only."""
        self.cost_this_turn = cost

    def set_cost_this_combat(self, cost: int) -> None:
        """Set a temporary cost for this combat."""
        self.cost_this_combat = cost

    def clear_turn_modifiers(self) -> None:
        """Clear per-turn modifiers (called at end of turn)."""
        self.cost_this_turn = None

    def clear_combat_modifiers(self) -> None:
        """Clear per-combat modifiers (called at end of combat)."""
        self.cost_this_combat = None
        self.cost_this_turn = None

    def copy(self) -> CardInstance:
        """Create a copy of this card instance."""
        return CardInstance(
            data=self.data,
            upgraded=self.upgraded,
            cost_modifier=self.cost_modifier,
        )

    def __str__(self) -> str:
        cost_str = f"[{self.cost}]" if self.cost >= 0 else "[X]"
        return f"{self.name} {cost_str}"

    def __repr__(self) -> str:
        return f"CardInstance({self.name}, cost={self.cost}, upgraded={self.upgraded})"
