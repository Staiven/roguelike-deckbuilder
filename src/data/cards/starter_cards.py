"""Starter card definitions."""

from __future__ import annotations

from src.core.enums import CardType, CardRarity, TargetType, StatusEffectType
from src.core.effects import (
    DamageEffect,
    BlockEffect,
    DrawEffect,
    ApplyStatusEffect,
    CompositeEffect,
)
from src.entities.card import CardData, CardInstance


# =============================================================================
# COMMON STARTER CARDS (All Classes)
# =============================================================================

STRIKE = CardData(
    id="strike",
    name="Strike",
    card_type=CardType.ATTACK,
    rarity=CardRarity.STARTER,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=1,
    base_effects=[DamageEffect(base_damage=6)],
    description="Deal 6 damage.",
    upgraded_effects=[DamageEffect(base_damage=9)],
    upgraded_description="Deal 9 damage.",
)

DEFEND = CardData(
    id="defend",
    name="Defend",
    card_type=CardType.SKILL,
    rarity=CardRarity.STARTER,
    target_type=TargetType.SELF,
    base_cost=1,
    base_effects=[BlockEffect(base_block=5)],
    description="Gain 5 Block.",
    upgraded_effects=[BlockEffect(base_block=8)],
    upgraded_description="Gain 8 Block.",
)


# =============================================================================
# WARRIOR STARTER CARDS
# =============================================================================

BASH = CardData(
    id="bash",
    name="Bash",
    card_type=CardType.ATTACK,
    rarity=CardRarity.STARTER,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=2,
    base_effects=[
        DamageEffect(base_damage=8),
        ApplyStatusEffect(StatusEffectType.VULNERABLE, amount=2),
    ],
    description="Deal 8 damage. Apply 2 Vulnerable.",
    upgraded_effects=[
        DamageEffect(base_damage=10),
        ApplyStatusEffect(StatusEffectType.VULNERABLE, amount=3),
    ],
    upgraded_description="Deal 10 damage. Apply 3 Vulnerable.",
)


# =============================================================================
# MAGE (SILENT) STARTER CARDS
# =============================================================================

NEUTRALIZE = CardData(
    id="neutralize",
    name="Neutralize",
    card_type=CardType.ATTACK,
    rarity=CardRarity.STARTER,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=0,
    base_effects=[
        DamageEffect(base_damage=3),
        ApplyStatusEffect(StatusEffectType.WEAK, amount=1),
    ],
    description="Deal 3 damage. Apply 1 Weak.",
    upgraded_effects=[
        DamageEffect(base_damage=4),
        ApplyStatusEffect(StatusEffectType.WEAK, amount=2),
    ],
    upgraded_description="Deal 4 damage. Apply 2 Weak.",
)

SURVIVOR = CardData(
    id="survivor",
    name="Survivor",
    card_type=CardType.SKILL,
    rarity=CardRarity.STARTER,
    target_type=TargetType.SELF,
    base_cost=1,
    base_effects=[BlockEffect(base_block=8)],  # Also discards a card, but simplified
    description="Gain 8 Block. Discard 1 card.",
    upgraded_effects=[BlockEffect(base_block=11)],
    upgraded_description="Gain 11 Block. Discard 1 card.",
)


# =============================================================================
# DECK CREATION FUNCTIONS
# =============================================================================

def create_starter_deck_warrior() -> list[CardInstance]:
    """Create the Ironclad's starting deck."""
    deck: list[CardInstance] = []

    # 5 Strikes
    for _ in range(5):
        deck.append(CardInstance(data=STRIKE))

    # 4 Defends
    for _ in range(4):
        deck.append(CardInstance(data=DEFEND))

    # 1 Bash
    deck.append(CardInstance(data=BASH))

    return deck


def create_starter_deck_mage() -> list[CardInstance]:
    """Create the Silent's starting deck."""
    deck: list[CardInstance] = []

    # 5 Strikes
    for _ in range(5):
        deck.append(CardInstance(data=STRIKE))

    # 5 Defends
    for _ in range(5):
        deck.append(CardInstance(data=DEFEND))

    # 1 Neutralize
    deck.append(CardInstance(data=NEUTRALIZE))

    # 1 Survivor
    deck.append(CardInstance(data=SURVIVOR))

    return deck


# Card registry for lookup
STARTER_CARD_REGISTRY: dict[str, CardData] = {
    "strike": STRIKE,
    "defend": DEFEND,
    "bash": BASH,
    "neutralize": NEUTRALIZE,
    "survivor": SURVIVOR,
}


def get_starter_card(card_id: str) -> CardData | None:
    """Get a starter card by ID."""
    return STARTER_CARD_REGISTRY.get(card_id)
