"""Act 1 enemy definitions."""

from __future__ import annotations
import random
from typing import TYPE_CHECKING

from src.core.enums import IntentType, StatusEffectType
from src.entities.enemy import Enemy, EnemyData, Intent

if TYPE_CHECKING:
    from src.combat.combat_manager import CombatState


# =============================================================================
# ENEMY AI FUNCTIONS
# =============================================================================

def jaw_worm_ai(enemy: Enemy, state: CombatState) -> Intent:
    """Jaw Worm AI - cycles between chomp, bellow, and thrash."""
    move_count = enemy.turn_count % 3

    if move_count == 0:
        # Chomp
        return Intent(IntentType.ATTACK, damage=11)
    elif move_count == 1:
        # Bellow (block + strength)
        return Intent(IntentType.ATTACK_BUFF, damage=0, block=6, buff_amount=3)
    else:
        # Thrash
        return Intent(IntentType.ATTACK_DEFEND, damage=7, block=5)


def cultist_ai(enemy: Enemy, state: CombatState) -> Intent:
    """Cultist AI - gains ritual (strength) then attacks."""
    if enemy.turn_count == 0:
        # First turn: Incantation (gain strength each turn)
        return Intent(IntentType.BUFF, buff_amount=3)
    else:
        # Dark Strike
        return Intent(IntentType.ATTACK, damage=6)


def louse_ai(enemy: Enemy, state: CombatState) -> Intent:
    """Louse AI - mostly attacks with occasional curl up (block)."""
    # Random damage between 5-7
    damage = random.randint(5, 7)

    if random.random() < 0.25 and enemy.block == 0:
        # Curl Up
        return Intent(IntentType.DEFEND, block=random.randint(3, 7))
    else:
        # Bite
        return Intent(IntentType.ATTACK, damage=damage)


def acid_slime_ai(enemy: Enemy, state: CombatState) -> Intent:
    """Acid Slime AI - attacks and applies weak."""
    if random.random() < 0.3:
        # Lick (apply weak)
        return Intent(IntentType.DEBUFF, debuff_amount=1)
    else:
        # Tackle
        return Intent(IntentType.ATTACK, damage=10)


def spike_slime_ai(enemy: Enemy, state: CombatState) -> Intent:
    """Spike Slime AI - attacks and applies frail."""
    if random.random() < 0.3:
        # Lick (apply frail)
        return Intent(IntentType.DEBUFF, debuff_amount=1)
    else:
        # Tackle
        return Intent(IntentType.ATTACK, damage=8)


def gremlin_nob_ai(enemy: Enemy, state: CombatState) -> Intent:
    """Gremlin Nob AI - enrages when you play skills."""
    if enemy.turn_count == 0:
        # Bellow (gain anger - strength when player plays skill)
        return Intent(IntentType.BUFF, buff_amount=2)
    elif enemy.turn_count % 3 == 0:
        # Skull Bash
        return Intent(IntentType.ATTACK_DEBUFF, damage=6, debuff_amount=2)
    else:
        # Rush
        return Intent(IntentType.ATTACK, damage=14)


def lagavulin_ai(enemy: Enemy, state: CombatState) -> Intent:
    """Lagavulin AI - sleeps for 3 turns then wakes up angry."""
    if enemy.turn_count < 3 and enemy.current_hp == enemy.max_hp:
        return Intent(IntentType.SLEEPING)
    elif enemy.turn_count % 3 == 0:
        # Siphon Soul (debuff strength and dexterity)
        return Intent(IntentType.DEBUFF, debuff_amount=1)
    else:
        # Attack
        return Intent(IntentType.ATTACK, damage=18)


def sentry_ai(enemy: Enemy, state: CombatState) -> Intent:
    """Sentry AI - alternates between beam and add dazed."""
    if enemy.turn_count % 2 == 0:
        # Beam
        return Intent(IntentType.ATTACK, damage=9)
    else:
        # Bolt (add status to deck)
        return Intent(IntentType.DEBUFF)


def slime_boss_ai(enemy: Enemy, state: CombatState) -> Intent:
    """Slime Boss AI - slams then prepares (goo)."""
    if enemy.turn_count % 2 == 0:
        # Goop Spray (add slimed to deck)
        return Intent(IntentType.DEBUFF)
    else:
        # Slam
        return Intent(IntentType.ATTACK, damage=35)


# =============================================================================
# ENEMY DATA DEFINITIONS
# =============================================================================

JAW_WORM = EnemyData(
    id="jaw_worm",
    name="Jaw Worm",
    max_hp_range=(40, 44),
    ai_function=jaw_worm_ai,
)

CULTIST = EnemyData(
    id="cultist",
    name="Cultist",
    max_hp_range=(48, 54),
    ai_function=cultist_ai,
)

LOUSE_RED = EnemyData(
    id="louse_red",
    name="Red Louse",
    max_hp_range=(10, 15),
    ai_function=louse_ai,
)

LOUSE_GREEN = EnemyData(
    id="louse_green",
    name="Green Louse",
    max_hp_range=(11, 17),
    ai_function=louse_ai,
)

ACID_SLIME_M = EnemyData(
    id="acid_slime_m",
    name="Acid Slime (M)",
    max_hp_range=(28, 32),
    ai_function=acid_slime_ai,
)

SPIKE_SLIME_M = EnemyData(
    id="spike_slime_m",
    name="Spike Slime (M)",
    max_hp_range=(28, 32),
    ai_function=spike_slime_ai,
)


# =============================================================================
# ELITE ENEMY DATA
# =============================================================================

GREMLIN_NOB = EnemyData(
    id="gremlin_nob",
    name="Gremlin Nob",
    max_hp_range=(82, 86),
    ai_function=gremlin_nob_ai,
)

LAGAVULIN = EnemyData(
    id="lagavulin",
    name="Lagavulin",
    max_hp_range=(109, 111),
    ai_function=lagavulin_ai,
)

SENTRY = EnemyData(
    id="sentry",
    name="Sentry",
    max_hp_range=(38, 42),
    ai_function=sentry_ai,
)


# =============================================================================
# BOSS ENEMY DATA
# =============================================================================

SLIME_BOSS = EnemyData(
    id="slime_boss",
    name="Slime Boss",
    max_hp_range=(140, 140),
    ai_function=slime_boss_ai,
)


# =============================================================================
# ENEMY REGISTRY AND HELPER FUNCTIONS
# =============================================================================

ENEMY_REGISTRY: dict[str, EnemyData] = {
    "jaw_worm": JAW_WORM,
    "cultist": CULTIST,
    "louse_red": LOUSE_RED,
    "louse_green": LOUSE_GREEN,
    "acid_slime_m": ACID_SLIME_M,
    "spike_slime_m": SPIKE_SLIME_M,
    "gremlin_nob": GREMLIN_NOB,
    "lagavulin": LAGAVULIN,
    "sentry": SENTRY,
    "slime_boss": SLIME_BOSS,
}


def create_enemy(enemy_id: str, ascension: int = 0) -> Enemy | None:
    """Create an enemy instance by ID."""
    data = ENEMY_REGISTRY.get(enemy_id)
    if data:
        return Enemy.from_data(data, ascension)
    return None


# Encounter pools
ACT1_EASY_POOL = [JAW_WORM, CULTIST]
ACT1_NORMAL_POOL = [LOUSE_RED, LOUSE_GREEN, ACID_SLIME_M, SPIKE_SLIME_M]
ACT1_ELITE_POOL = [GREMLIN_NOB, LAGAVULIN]


def get_random_act1_encounter(difficulty: str = "normal", ascension: int = 0) -> list[Enemy]:
    """Get a random Act 1 enemy encounter."""
    if difficulty == "easy":
        enemy_data = random.choice(ACT1_EASY_POOL)
        return [Enemy.from_data(enemy_data, ascension)]
    else:
        # Normal encounters can be 1-2 enemies
        num_enemies = random.randint(1, 2)
        enemies: list[Enemy] = []

        for _ in range(num_enemies):
            enemy_data = random.choice(ACT1_NORMAL_POOL)
            enemies.append(Enemy.from_data(enemy_data, ascension))

        return enemies


def get_random_act1_elite(ascension: int = 0) -> list[Enemy]:
    """Get a random Act 1 elite encounter."""
    enemy_data = random.choice(ACT1_ELITE_POOL)

    if enemy_data == SENTRY:
        # Sentries come in pairs
        return [
            Enemy.from_data(SENTRY, ascension),
            Enemy.from_data(SENTRY, ascension),
        ]
    else:
        return [Enemy.from_data(enemy_data, ascension)]


def get_act1_boss(ascension: int = 0) -> list[Enemy]:
    """Get the Act 1 boss."""
    return [Enemy.from_data(SLIME_BOSS, ascension)]
