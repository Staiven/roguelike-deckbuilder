"""Common card definitions."""

from __future__ import annotations

from src.core.enums import CardType, CardRarity, TargetType, StatusEffectType
from src.core.effects import (
    DamageEffect,
    BlockEffect,
    DrawEffect,
    ApplyStatusEffect,
    GainEnergyEffect,
)
from src.entities.card import CardData, CardInstance


# =============================================================================
# WARRIOR COMMON CARDS
# =============================================================================

ANGER = CardData(
    id="anger",
    name="Anger",
    card_type=CardType.ATTACK,
    rarity=CardRarity.COMMON,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=0,
    base_effects=[DamageEffect(base_damage=6)],
    description="Deal 6 damage. Add a copy of this card to your discard pile.",
    upgraded_effects=[DamageEffect(base_damage=8)],
    upgraded_description="Deal 8 damage. Add a copy of this card to your discard pile.",
)

CLEAVE = CardData(
    id="cleave",
    name="Cleave",
    card_type=CardType.ATTACK,
    rarity=CardRarity.COMMON,
    target_type=TargetType.ALL_ENEMIES,
    base_cost=1,
    base_effects=[DamageEffect(base_damage=8)],
    description="Deal 8 damage to ALL enemies.",
    upgraded_effects=[DamageEffect(base_damage=11)],
    upgraded_description="Deal 11 damage to ALL enemies.",
)

CLOTHESLINE = CardData(
    id="clothesline",
    name="Clothesline",
    card_type=CardType.ATTACK,
    rarity=CardRarity.COMMON,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=2,
    base_effects=[
        DamageEffect(base_damage=12),
        ApplyStatusEffect(StatusEffectType.WEAK, amount=2),
    ],
    description="Deal 12 damage. Apply 2 Weak.",
    upgraded_effects=[
        DamageEffect(base_damage=14),
        ApplyStatusEffect(StatusEffectType.WEAK, amount=3),
    ],
    upgraded_description="Deal 14 damage. Apply 3 Weak.",
)

IRON_WAVE = CardData(
    id="iron_wave",
    name="Iron Wave",
    card_type=CardType.ATTACK,
    rarity=CardRarity.COMMON,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=1,
    base_effects=[
        DamageEffect(base_damage=5),
        BlockEffect(base_block=5),
    ],
    description="Gain 5 Block. Deal 5 damage.",
    upgraded_effects=[
        DamageEffect(base_damage=7),
        BlockEffect(base_block=7),
    ],
    upgraded_description="Gain 7 Block. Deal 7 damage.",
)

POMMEL_STRIKE = CardData(
    id="pommel_strike",
    name="Pommel Strike",
    card_type=CardType.ATTACK,
    rarity=CardRarity.COMMON,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=1,
    base_effects=[
        DamageEffect(base_damage=9),
        DrawEffect(cards=1),
    ],
    description="Deal 9 damage. Draw 1 card.",
    upgraded_effects=[
        DamageEffect(base_damage=10),
        DrawEffect(cards=2),
    ],
    upgraded_description="Deal 10 damage. Draw 2 cards.",
)

SHRUG_IT_OFF = CardData(
    id="shrug_it_off",
    name="Shrug It Off",
    card_type=CardType.SKILL,
    rarity=CardRarity.COMMON,
    target_type=TargetType.SELF,
    base_cost=1,
    base_effects=[
        BlockEffect(base_block=8),
        DrawEffect(cards=1),
    ],
    description="Gain 8 Block. Draw 1 card.",
    upgraded_effects=[
        BlockEffect(base_block=11),
        DrawEffect(cards=1),
    ],
    upgraded_description="Gain 11 Block. Draw 1 card.",
)

SWORD_BOOMERANG = CardData(
    id="sword_boomerang",
    name="Sword Boomerang",
    card_type=CardType.ATTACK,
    rarity=CardRarity.COMMON,
    target_type=TargetType.RANDOM_ENEMY,
    base_cost=1,
    base_effects=[DamageEffect(base_damage=3, times=3)],
    description="Deal 3 damage to a random enemy 3 times.",
    upgraded_effects=[DamageEffect(base_damage=3, times=4)],
    upgraded_description="Deal 3 damage to a random enemy 4 times.",
)

THUNDERCLAP = CardData(
    id="thunderclap",
    name="Thunderclap",
    card_type=CardType.ATTACK,
    rarity=CardRarity.COMMON,
    target_type=TargetType.ALL_ENEMIES,
    base_cost=1,
    base_effects=[
        DamageEffect(base_damage=4),
        ApplyStatusEffect(StatusEffectType.VULNERABLE, amount=1),
    ],
    description="Deal 4 damage and apply 1 Vulnerable to ALL enemies.",
    upgraded_effects=[
        DamageEffect(base_damage=7),
        ApplyStatusEffect(StatusEffectType.VULNERABLE, amount=1),
    ],
    upgraded_description="Deal 7 damage and apply 1 Vulnerable to ALL enemies.",
)


# =============================================================================
# MAGE (SILENT) COMMON CARDS
# =============================================================================

BLADE_DANCE = CardData(
    id="blade_dance",
    name="Blade Dance",
    card_type=CardType.SKILL,
    rarity=CardRarity.COMMON,
    target_type=TargetType.NONE,
    base_cost=1,
    base_effects=[],  # Would add shivs to hand
    description="Add 3 Shivs to your hand.",
    upgraded_effects=[],
    upgraded_description="Add 4 Shivs to your hand.",
)

DEADLY_POISON = CardData(
    id="deadly_poison",
    name="Deadly Poison",
    card_type=CardType.SKILL,
    rarity=CardRarity.COMMON,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=1,
    base_effects=[ApplyStatusEffect(StatusEffectType.POISON, amount=5)],
    description="Apply 5 Poison.",
    upgraded_effects=[ApplyStatusEffect(StatusEffectType.POISON, amount=7)],
    upgraded_description="Apply 7 Poison.",
)

QUICK_SLASH = CardData(
    id="quick_slash",
    name="Quick Slash",
    card_type=CardType.ATTACK,
    rarity=CardRarity.COMMON,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=1,
    base_effects=[
        DamageEffect(base_damage=8),
        DrawEffect(cards=1),
    ],
    description="Deal 8 damage. Draw 1 card.",
    upgraded_effects=[
        DamageEffect(base_damage=12),
        DrawEffect(cards=1),
    ],
    upgraded_description="Deal 12 damage. Draw 1 card.",
)

SLICE = CardData(
    id="slice",
    name="Slice",
    card_type=CardType.ATTACK,
    rarity=CardRarity.COMMON,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=0,
    base_effects=[DamageEffect(base_damage=6)],
    description="Deal 6 damage.",
    upgraded_effects=[DamageEffect(base_damage=9)],
    upgraded_description="Deal 9 damage.",
)

SNEAKY_STRIKE = CardData(
    id="sneaky_strike",
    name="Sneaky Strike",
    card_type=CardType.ATTACK,
    rarity=CardRarity.COMMON,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=2,
    base_effects=[DamageEffect(base_damage=12)],
    description="Deal 12 damage. If you have discarded a card this turn, costs 0.",
    upgraded_effects=[DamageEffect(base_damage=16)],
    upgraded_description="Deal 16 damage. If you have discarded a card this turn, costs 0.",
)

SUCKER_PUNCH = CardData(
    id="sucker_punch",
    name="Sucker Punch",
    card_type=CardType.ATTACK,
    rarity=CardRarity.COMMON,
    target_type=TargetType.SINGLE_ENEMY,
    base_cost=1,
    base_effects=[
        DamageEffect(base_damage=7),
        ApplyStatusEffect(StatusEffectType.WEAK, amount=1),
    ],
    description="Deal 7 damage. Apply 1 Weak.",
    upgraded_effects=[
        DamageEffect(base_damage=9),
        ApplyStatusEffect(StatusEffectType.WEAK, amount=2),
    ],
    upgraded_description="Deal 9 damage. Apply 2 Weak.",
)


# =============================================================================
# CARD REGISTRY
# =============================================================================

COMMON_CARD_REGISTRY: dict[str, CardData] = {
    # Warrior
    "anger": ANGER,
    "cleave": CLEAVE,
    "clothesline": CLOTHESLINE,
    "iron_wave": IRON_WAVE,
    "pommel_strike": POMMEL_STRIKE,
    "shrug_it_off": SHRUG_IT_OFF,
    "sword_boomerang": SWORD_BOOMERANG,
    "thunderclap": THUNDERCLAP,
    # Mage
    "blade_dance": BLADE_DANCE,
    "deadly_poison": DEADLY_POISON,
    "quick_slash": QUICK_SLASH,
    "slice": SLICE,
    "sneaky_strike": SNEAKY_STRIKE,
    "sucker_punch": SUCKER_PUNCH,
}


def get_common_card(card_id: str) -> CardData | None:
    """Get a common card by ID."""
    return COMMON_CARD_REGISTRY.get(card_id)


def get_all_warrior_commons() -> list[CardData]:
    """Get all warrior common cards."""
    return [ANGER, CLEAVE, CLOTHESLINE, IRON_WAVE, POMMEL_STRIKE, SHRUG_IT_OFF, SWORD_BOOMERANG, THUNDERCLAP]


def get_all_mage_commons() -> list[CardData]:
    """Get all mage common cards."""
    return [BLADE_DANCE, DEADLY_POISON, QUICK_SLASH, SLICE, SNEAKY_STRIKE, SUCKER_PUNCH]
