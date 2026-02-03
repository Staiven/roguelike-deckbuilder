"""Common relic definitions."""

from __future__ import annotations
from typing import TYPE_CHECKING

from src.core.enums import RelicRarity, StatusEffectType
from src.core.events import EventType, GameEvent
from src.entities.relic import RelicData, RelicInstance, RelicTrigger

if TYPE_CHECKING:
    from src.entities.player import Player


# =============================================================================
# STARTER RELICS
# =============================================================================

def _burning_blood_effect(relic: RelicInstance, event: GameEvent, player: Player) -> None:
    """Heal 6 HP at the end of combat."""
    if event.data.get("victory", False):
        player.heal(6)


BURNING_BLOOD = RelicData(
    id="burning_blood",
    name="Burning Blood",
    rarity=RelicRarity.STARTER,
    description="At the end of combat, heal 6 HP.",
    trigger=RelicTrigger.COMBAT_END,
    effect=_burning_blood_effect,
)


def _ring_of_snake_effect(relic: RelicInstance, event: GameEvent, player: Player) -> None:
    """Draw 2 extra cards at the start of combat."""
    deck_manager = event.data.get("deck_manager")
    if deck_manager is not None:
        deck_manager.draw(2)


RING_OF_THE_SNAKE = RelicData(
    id="ring_of_the_snake",
    name="Ring of the Snake",
    rarity=RelicRarity.STARTER,
    description="At the start of combat, draw 2 additional cards.",
    trigger=RelicTrigger.COMBAT_START,
    effect=_ring_of_snake_effect,
)


CRACKED_CORE = RelicData(
    id="cracked_core",
    name="Cracked Core",
    rarity=RelicRarity.STARTER,
    description="At the start of combat, Channel 1 Lightning orb.",
    trigger=RelicTrigger.COMBAT_START,
    effect=None,  # Would need orb system
)


# =============================================================================
# COMMON RELICS
# =============================================================================

def _anchor_effect(relic: RelicInstance, event: GameEvent, player: Player) -> None:
    """Start each combat with 10 block."""
    player.block += 10


ANCHOR = RelicData(
    id="anchor",
    name="Anchor",
    rarity=RelicRarity.COMMON,
    description="Start each combat with 10 Block.",
    trigger=RelicTrigger.COMBAT_START,
    effect=_anchor_effect,
)


def _ancient_tea_set_effect(relic: RelicInstance, event: GameEvent, player: Player) -> None:
    """Gain 2 energy on the first turn after resting."""
    # Counter is set to 1 when resting, then gives energy at next combat start
    if relic.counter > 0:
        player.energy += 2
        relic.reset_counter()


ANCIENT_TEA_SET = RelicData(
    id="ancient_tea_set",
    name="Ancient Tea Set",
    rarity=RelicRarity.COMMON,
    description="Whenever you enter a Rest Site, start the next combat with 2 extra Energy.",
    trigger=RelicTrigger.COMBAT_START,
    effect=_ancient_tea_set_effect,
    counter_based=True,
)


def _bag_of_marbles_effect(relic: RelicInstance, event: GameEvent, player: Player) -> None:
    """Apply 1 Vulnerable to all enemies at the start of combat."""
    enemies = event.data.get("enemies", [])
    for enemy in enemies:
        current = enemy.status_effects.get(StatusEffectType.VULNERABLE, 0)
        enemy.status_effects[StatusEffectType.VULNERABLE] = current + 1


BAG_OF_MARBLES = RelicData(
    id="bag_of_marbles",
    name="Bag of Marbles",
    rarity=RelicRarity.COMMON,
    description="At the start of combat, apply 1 Vulnerable to ALL enemies.",
    trigger=RelicTrigger.COMBAT_START,
    effect=_bag_of_marbles_effect,
)


def _blood_vial_effect(relic: RelicInstance, event: GameEvent, player: Player) -> None:
    """Heal 2 HP at the start of combat."""
    player.heal(2)


BLOOD_VIAL = RelicData(
    id="blood_vial",
    name="Blood Vial",
    rarity=RelicRarity.COMMON,
    description="At the start of combat, heal 2 HP.",
    trigger=RelicTrigger.COMBAT_START,
    effect=_blood_vial_effect,
)


def _bronze_scales_effect(relic: RelicInstance, event: GameEvent, player: Player) -> None:
    """Deal 3 damage when attacked."""
    # Thorns effect handled via status
    current = player.status_effects.get(StatusEffectType.THORNS, 0)
    player.status_effects[StatusEffectType.THORNS] = current + 3


BRONZE_SCALES = RelicData(
    id="bronze_scales",
    name="Bronze Scales",
    rarity=RelicRarity.COMMON,
    description="Start each combat with 3 Thorns.",
    trigger=RelicTrigger.COMBAT_START,
    effect=_bronze_scales_effect,
)


def _centennial_puzzle_effect(relic: RelicInstance, event: GameEvent, player: Player) -> None:
    """Draw 3 cards the first time you take damage each combat."""
    # Counter tracks if already triggered this combat (reset at combat start)
    if relic.counter == 0:
        relic.increment_counter()
        # Access deck_manager through player's combat reference
        if hasattr(player, '_deck_manager') and player._deck_manager is not None:
            player._deck_manager.draw(3)


CENTENNIAL_PUZZLE = RelicData(
    id="centennial_puzzle",
    name="Centennial Puzzle",
    rarity=RelicRarity.COMMON,
    description="The first time you lose HP each combat, draw 3 cards.",
    trigger=RelicTrigger.ON_HP_LOSS,
    effect=_centennial_puzzle_effect,
    counter_based=True,
    max_counter=1,
)


def _vajra_effect(relic: RelicInstance, event: GameEvent, player: Player) -> None:
    """Start each combat with 1 Strength."""
    current = player.status_effects.get(StatusEffectType.STRENGTH, 0)
    player.status_effects[StatusEffectType.STRENGTH] = current + 1


VAJRA = RelicData(
    id="vajra",
    name="Vajra",
    rarity=RelicRarity.COMMON,
    description="Start each combat with 1 Strength.",
    trigger=RelicTrigger.COMBAT_START,
    effect=_vajra_effect,
)


# =============================================================================
# RELIC REGISTRY
# =============================================================================

RELIC_REGISTRY: dict[str, RelicData] = {
    "burning_blood": BURNING_BLOOD,
    "ring_of_the_snake": RING_OF_THE_SNAKE,
    "cracked_core": CRACKED_CORE,
    "anchor": ANCHOR,
    "ancient_tea_set": ANCIENT_TEA_SET,
    "bag_of_marbles": BAG_OF_MARBLES,
    "blood_vial": BLOOD_VIAL,
    "bronze_scales": BRONZE_SCALES,
    "centennial_puzzle": CENTENNIAL_PUZZLE,
    "vajra": VAJRA,
}


def get_relic(relic_id: str) -> RelicData | None:
    """Get a relic by ID."""
    return RELIC_REGISTRY.get(relic_id)


def create_relic_instance(relic_id: str) -> RelicInstance | None:
    """Create a relic instance by ID."""
    data = get_relic(relic_id)
    if data:
        return RelicInstance(data=data)
    return None


def create_starter_relic_warrior() -> RelicInstance:
    """Create the Ironclad's starting relic."""
    return RelicInstance(data=BURNING_BLOOD)


def create_starter_relic_mage() -> RelicInstance:
    """Create the Silent's starting relic."""
    return RelicInstance(data=RING_OF_THE_SNAKE)


def get_random_common_relic() -> RelicInstance:
    """Get a random common relic."""
    import random
    common_relics = [
        ANCHOR, ANCIENT_TEA_SET, BAG_OF_MARBLES,
        BLOOD_VIAL, BRONZE_SCALES, CENTENNIAL_PUZZLE, VAJRA,
    ]
    data = random.choice(common_relics)
    return RelicInstance(data=data)
