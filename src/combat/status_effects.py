"""Status effects (buffs and debuffs) system."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

from src.core.enums import StatusEffectType

if TYPE_CHECKING:
    from src.entities.player import Player
    from src.entities.enemy import Enemy


class StackType(Enum):
    """How a status effect stacks when applied multiple times."""
    INTENSITY = auto()    # Amount increases (e.g., Strength)
    DURATION = auto()     # Duration increases (e.g., Vulnerable)
    COUNTER = auto()      # Special counter-based (e.g., Ritual)
    NONE = auto()         # Doesn't stack (e.g., some unique effects)


@dataclass
class StatusEffect:
    """Definition of a status effect."""
    effect_type: StatusEffectType
    name: str
    description: str
    is_debuff: bool
    stack_type: StackType
    decrements_at_end_of_turn: bool = False
    removes_at_zero: bool = True


# Standard status effect definitions
STRENGTH = StatusEffect(
    effect_type=StatusEffectType.STRENGTH,
    name="Strength",
    description="Increases attack damage by {amount}.",
    is_debuff=False,
    stack_type=StackType.INTENSITY,
)

DEXTERITY = StatusEffect(
    effect_type=StatusEffectType.DEXTERITY,
    name="Dexterity",
    description="Increases block gained by {amount}.",
    is_debuff=False,
    stack_type=StackType.INTENSITY,
)

VULNERABLE = StatusEffect(
    effect_type=StatusEffectType.VULNERABLE,
    name="Vulnerable",
    description="Takes 50% more damage from attacks. Lasts {amount} turn(s).",
    is_debuff=True,
    stack_type=StackType.DURATION,
    decrements_at_end_of_turn=True,
)

WEAK = StatusEffect(
    effect_type=StatusEffectType.WEAK,
    name="Weak",
    description="Deals 25% less attack damage. Lasts {amount} turn(s).",
    is_debuff=True,
    stack_type=StackType.DURATION,
    decrements_at_end_of_turn=True,
)

FRAIL = StatusEffect(
    effect_type=StatusEffectType.FRAIL,
    name="Frail",
    description="Gains 25% less block from cards. Lasts {amount} turn(s).",
    is_debuff=True,
    stack_type=StackType.DURATION,
    decrements_at_end_of_turn=True,
)

POISON = StatusEffect(
    effect_type=StatusEffectType.POISON,
    name="Poison",
    description="At the end of turn, lose {amount} HP and reduce Poison by 1.",
    is_debuff=True,
    stack_type=StackType.INTENSITY,
    decrements_at_end_of_turn=True,
)

ARTIFACT = StatusEffect(
    effect_type=StatusEffectType.ARTIFACT,
    name="Artifact",
    description="Negates {amount} debuff application(s).",
    is_debuff=False,
    stack_type=StackType.COUNTER,
)

THORNS = StatusEffect(
    effect_type=StatusEffectType.THORNS,
    name="Thorns",
    description="When attacked, deal {amount} damage back.",
    is_debuff=False,
    stack_type=StackType.INTENSITY,
)

METALLICIZE = StatusEffect(
    effect_type=StatusEffectType.METALLICIZE,
    name="Metallicize",
    description="At the end of turn, gain {amount} Block.",
    is_debuff=False,
    stack_type=StackType.INTENSITY,
)

REGEN = StatusEffect(
    effect_type=StatusEffectType.REGEN,
    name="Regeneration",
    description="Heal {amount} HP at the end of turn, then reduce by 1.",
    is_debuff=False,
    stack_type=StackType.INTENSITY,
    decrements_at_end_of_turn=True,
)

INTANGIBLE = StatusEffect(
    effect_type=StatusEffectType.INTANGIBLE,
    name="Intangible",
    description="Reduce ALL damage taken to 1. Lasts {amount} turn(s).",
    is_debuff=False,
    stack_type=StackType.DURATION,
    decrements_at_end_of_turn=True,
)

PLATED_ARMOR = StatusEffect(
    effect_type=StatusEffectType.PLATED_ARMOR,
    name="Plated Armor",
    description="At end of turn, gain {amount} Block. Taking unblocked damage reduces this by 1.",
    is_debuff=False,
    stack_type=StackType.INTENSITY,
)

# Registry for looking up status effects by type
STATUS_EFFECT_REGISTRY: dict[StatusEffectType, StatusEffect] = {
    StatusEffectType.STRENGTH: STRENGTH,
    StatusEffectType.DEXTERITY: DEXTERITY,
    StatusEffectType.VULNERABLE: VULNERABLE,
    StatusEffectType.WEAK: WEAK,
    StatusEffectType.FRAIL: FRAIL,
    StatusEffectType.POISON: POISON,
    StatusEffectType.ARTIFACT: ARTIFACT,
    StatusEffectType.THORNS: THORNS,
    StatusEffectType.METALLICIZE: METALLICIZE,
    StatusEffectType.REGEN: REGEN,
    StatusEffectType.INTANGIBLE: INTANGIBLE,
    StatusEffectType.PLATED_ARMOR: PLATED_ARMOR,
}


def get_status_effect(effect_type: StatusEffectType) -> StatusEffect | None:
    """Get the status effect definition for a type."""
    return STATUS_EFFECT_REGISTRY.get(effect_type)


def get_status_description(effect_type: StatusEffectType, amount: int) -> str:
    """Get a formatted description for a status effect with an amount."""
    effect = get_status_effect(effect_type)
    if effect:
        return effect.description.format(amount=amount)
    return f"{effect_type.name}: {amount}"


def is_debuff(effect_type: StatusEffectType) -> bool:
    """Check if a status effect type is a debuff."""
    effect = get_status_effect(effect_type)
    return effect.is_debuff if effect else False


def apply_status_to_entity(
    entity: Player | Enemy,
    effect_type: StatusEffectType,
    amount: int
) -> bool:
    """
    Apply a status effect to an entity.

    Handles artifact blocking for debuffs.

    Returns True if the effect was applied, False if blocked.
    """
    # Check for artifact blocking debuffs
    if is_debuff(effect_type):
        artifact_count = entity.status_effects.get(StatusEffectType.ARTIFACT, 0)
        if artifact_count > 0:
            entity.status_effects[StatusEffectType.ARTIFACT] = artifact_count - 1
            if entity.status_effects[StatusEffectType.ARTIFACT] <= 0:
                del entity.status_effects[StatusEffectType.ARTIFACT]
            return False

    # Apply the effect
    current = entity.status_effects.get(effect_type, 0)
    entity.status_effects[effect_type] = current + amount

    return True


def remove_status_from_entity(
    entity: Player | Enemy,
    effect_type: StatusEffectType
) -> bool:
    """
    Remove a status effect from an entity.

    Returns True if the effect existed and was removed.
    """
    if effect_type in entity.status_effects:
        del entity.status_effects[effect_type]
        return True
    return False


def process_end_of_turn_effects(entity: Player | Enemy) -> dict[str, int]:
    """
    Process status effects at the end of turn.

    Returns a dict of effects that were processed.
    """
    results: dict[str, int] = {}

    # Process metallicize
    metallicize = entity.status_effects.get(StatusEffectType.METALLICIZE, 0)
    if metallicize > 0:
        entity.block += metallicize
        results["block_gained"] = metallicize

    # Process regen
    regen = entity.status_effects.get(StatusEffectType.REGEN, 0)
    if regen > 0:
        healed = min(regen, entity.max_hp - entity.current_hp)
        entity.current_hp += healed
        results["healed"] = healed
        entity.status_effects[StatusEffectType.REGEN] = regen - 1
        if entity.status_effects[StatusEffectType.REGEN] <= 0:
            del entity.status_effects[StatusEffectType.REGEN]

    # Process plated armor
    plated = entity.status_effects.get(StatusEffectType.PLATED_ARMOR, 0)
    if plated > 0:
        entity.block += plated
        results["plated_block"] = plated

    # Decrement duration-based effects
    for effect_type in [
        StatusEffectType.VULNERABLE,
        StatusEffectType.WEAK,
        StatusEffectType.FRAIL,
        StatusEffectType.INTANGIBLE,
    ]:
        if effect_type in entity.status_effects:
            entity.status_effects[effect_type] -= 1
            if entity.status_effects[effect_type] <= 0:
                del entity.status_effects[effect_type]

    return results
