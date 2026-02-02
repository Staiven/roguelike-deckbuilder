"""Core enumerations for the roguelike deck-builder game."""

from enum import Enum, auto


class CardType(Enum):
    """Types of cards in the game."""
    ATTACK = auto()
    SKILL = auto()
    POWER = auto()
    STATUS = auto()
    CURSE = auto()


class TargetType(Enum):
    """Targeting modes for cards and effects."""
    SINGLE_ENEMY = auto()
    ALL_ENEMIES = auto()
    SELF = auto()
    RANDOM_ENEMY = auto()
    NONE = auto()


class CardRarity(Enum):
    """Rarity levels for cards."""
    STARTER = auto()
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()


class RelicRarity(Enum):
    """Rarity levels for relics."""
    STARTER = auto()
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    BOSS = auto()
    SHOP = auto()
    EVENT = auto()


class MapNodeType(Enum):
    """Types of nodes on the map."""
    COMBAT = auto()
    ELITE = auto()
    REST = auto()
    SHOP = auto()
    EVENT = auto()
    BOSS = auto()
    TREASURE = auto()


class StatusEffectType(Enum):
    """Types of status effects (buffs and debuffs)."""
    # Buffs
    STRENGTH = auto()
    DEXTERITY = auto()
    ARTIFACT = auto()
    INTANGIBLE = auto()
    THORNS = auto()
    METALLICIZE = auto()
    PLATED_ARMOR = auto()
    REGEN = auto()

    # Debuffs
    VULNERABLE = auto()
    WEAK = auto()
    FRAIL = auto()
    POISON = auto()

    # Neutral
    RITUAL = auto()


class IntentType(Enum):
    """Enemy intent types shown to the player."""
    ATTACK = auto()
    DEFEND = auto()
    BUFF = auto()
    DEBUFF = auto()
    ATTACK_DEFEND = auto()
    ATTACK_BUFF = auto()
    ATTACK_DEBUFF = auto()
    UNKNOWN = auto()
    SLEEPING = auto()
