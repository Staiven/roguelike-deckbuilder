"""Tests for effect system."""

import pytest
from src.core.events import reset_event_bus
from src.core.enums import StatusEffectType
from src.core.effects import (
    DamageEffect,
    BlockEffect,
    DrawEffect,
    ApplyStatusEffect,
    HealEffect,
    CompositeEffect,
)
from src.entities.player import Player
from src.entities.enemy import Enemy, Intent, IntentType
from src.combat.combat_manager import CombatManager


@pytest.fixture(autouse=True)
def reset_events():
    """Reset event bus before each test."""
    reset_event_bus()


@pytest.fixture
def player() -> Player:
    """Create a test player."""
    return Player(
        name="Test Player",
        max_hp=80,
        current_hp=60,
        gold=99,
        max_energy=3,
        energy=3,
    )


@pytest.fixture
def enemy() -> Enemy:
    """Create a test enemy."""
    return Enemy(
        id="test_enemy",
        name="Test Enemy",
        max_hp=50,
        current_hp=50,
        intent=Intent(IntentType.ATTACK, damage=10),
    )


class TestDamageEffect:
    def test_basic_damage(self, player: Player, enemy: Enemy):
        """Test basic damage effect."""
        effect = DamageEffect(base_damage=10)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        result = effect.apply(state, player, enemy)

        assert enemy.current_hp == 40
        assert result["total_damage"] == 10

    def test_damage_blocked(self, player: Player, enemy: Enemy):
        """Test damage blocked by armor."""
        effect = DamageEffect(base_damage=10)
        enemy.block = 5

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        result = effect.apply(state, player, enemy)

        assert enemy.current_hp == 45  # 10 - 5 = 5 damage
        assert enemy.block == 0
        assert result["damage_dealt"][0]["blocked"] == 5

    def test_multi_hit_damage(self, player: Player, enemy: Enemy):
        """Test damage effect that hits multiple times."""
        effect = DamageEffect(base_damage=3, times=4)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        result = effect.apply(state, player, enemy)

        assert enemy.current_hp == 38  # 50 - (3 * 4) = 38
        assert result["total_damage"] == 12

    def test_damage_with_strength(self, player: Player, enemy: Enemy):
        """Test damage effect with strength buff."""
        effect = DamageEffect(base_damage=6)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        # Apply strength AFTER combat start (which clears status effects)
        player.status_effects[StatusEffectType.STRENGTH] = 3
        result = effect.apply(state, player, enemy)

        assert enemy.current_hp == 41  # 50 - (6 + 3) = 41

    def test_description(self):
        """Test damage effect description."""
        effect = DamageEffect(base_damage=6)
        assert effect.get_description() == "Deal 6 damage"

        effect_multi = DamageEffect(base_damage=3, times=3)
        assert effect_multi.get_description() == "Deal 3 damage 3 times"


class TestBlockEffect:
    def test_basic_block(self, player: Player, enemy: Enemy):
        """Test basic block gain."""
        effect = BlockEffect(base_block=5)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        result = effect.apply(state, player)

        assert player.block == 5
        assert result["block_gained"] == 5

    def test_block_with_dexterity(self, player: Player, enemy: Enemy):
        """Test block gain with dexterity buff."""
        effect = BlockEffect(base_block=5)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        # Apply dexterity AFTER combat start (which clears status effects)
        player.status_effects[StatusEffectType.DEXTERITY] = 2
        result = effect.apply(state, player)

        assert player.block == 7  # 5 + 2

    def test_block_with_frail(self, player: Player, enemy: Enemy):
        """Test block gain reduced by frail."""
        effect = BlockEffect(base_block=8)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        # Apply frail AFTER combat start (which clears status effects)
        player.status_effects[StatusEffectType.FRAIL] = 2
        result = effect.apply(state, player)

        assert player.block == 6  # 8 * 0.75 = 6

    def test_description(self):
        """Test block effect description."""
        effect = BlockEffect(base_block=5)
        assert effect.get_description() == "Gain 5 Block"


class TestApplyStatusEffect:
    def test_apply_vulnerable(self, player: Player, enemy: Enemy):
        """Test applying vulnerable debuff."""
        effect = ApplyStatusEffect(StatusEffectType.VULNERABLE, amount=2)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        effect.apply(state, player, enemy)

        assert enemy.status_effects[StatusEffectType.VULNERABLE] == 2

    def test_apply_strength(self, player: Player, enemy: Enemy):
        """Test applying strength buff."""
        effect = ApplyStatusEffect(StatusEffectType.STRENGTH, amount=2)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        effect.apply(state, player, player)

        assert player.status_effects[StatusEffectType.STRENGTH] == 2

    def test_stacking_status(self, player: Player, enemy: Enemy):
        """Test that status effects stack."""
        effect = ApplyStatusEffect(StatusEffectType.POISON, amount=3)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        effect.apply(state, player, enemy)
        effect.apply(state, player, enemy)

        assert enemy.status_effects[StatusEffectType.POISON] == 6

    def test_artifact_blocks_debuff(self, player: Player, enemy: Enemy):
        """Test that artifact blocks debuffs."""
        enemy.status_effects[StatusEffectType.ARTIFACT] = 1
        effect = ApplyStatusEffect(StatusEffectType.VULNERABLE, amount=2)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        effect.apply(state, player, enemy)

        assert StatusEffectType.VULNERABLE not in enemy.status_effects
        assert StatusEffectType.ARTIFACT not in enemy.status_effects  # Consumed

    def test_description(self):
        """Test status effect description."""
        effect = ApplyStatusEffect(StatusEffectType.VULNERABLE, amount=2)
        assert effect.get_description() == "Apply 2 Vulnerable"


class TestHealEffect:
    def test_basic_heal(self, player: Player, enemy: Enemy):
        """Test basic healing."""
        player.current_hp = 50
        effect = HealEffect(amount=10)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        result = effect.apply(state, player)

        assert player.current_hp == 60
        assert result["healed"] == 10

    def test_heal_capped_at_max(self, player: Player, enemy: Enemy):
        """Test healing doesn't exceed max HP."""
        player.current_hp = 75
        effect = HealEffect(amount=10)

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        result = effect.apply(state, player)

        assert player.current_hp == 80  # max HP
        assert result["healed"] == 5

    def test_description(self):
        """Test heal effect description."""
        effect = HealEffect(amount=6)
        assert effect.get_description() == "Heal 6 HP"


class TestCompositeEffect:
    def test_multiple_effects(self, player: Player, enemy: Enemy):
        """Test composite effect applies all sub-effects."""
        # Test a composite effect that damages enemy and applies vulnerable
        effect = CompositeEffect(effects=[
            DamageEffect(base_damage=6),
            ApplyStatusEffect(StatusEffectType.VULNERABLE, amount=2),
        ])

        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        initial_enemy_hp = enemy.current_hp
        result = effect.apply(state, player, enemy)

        assert enemy.current_hp == initial_enemy_hp - 6
        assert enemy.status_effects[StatusEffectType.VULNERABLE] == 2
        assert len(result["sub_effects"]) == 2

    def test_description(self):
        """Test composite effect description."""
        effect = CompositeEffect(effects=[
            DamageEffect(base_damage=6),
            BlockEffect(base_block=5),
        ])
        desc = effect.get_description()
        assert "Deal 6 damage" in desc
        assert "Gain 5 Block" in desc
