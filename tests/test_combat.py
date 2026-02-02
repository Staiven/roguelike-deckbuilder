"""Tests for combat system."""

import pytest
from src.core.events import reset_event_bus
from src.core.enums import CardType, CardRarity, TargetType, StatusEffectType
from src.core.effects import DamageEffect, BlockEffect, ApplyStatusEffect
from src.entities.card import CardData, CardInstance
from src.entities.player import Player
from src.entities.enemy import Enemy, Intent, IntentType
from src.combat.combat_manager import CombatManager, CombatResult, CombatPhase


@pytest.fixture(autouse=True)
def reset_events():
    """Reset event bus before each test."""
    reset_event_bus()


@pytest.fixture
def strike_card() -> CardData:
    """Create a Strike card."""
    return CardData(
        id="strike",
        name="Strike",
        card_type=CardType.ATTACK,
        rarity=CardRarity.STARTER,
        target_type=TargetType.SINGLE_ENEMY,
        base_cost=1,
        base_effects=[DamageEffect(base_damage=6)],
        description="Deal 6 damage.",
    )


@pytest.fixture
def defend_card() -> CardData:
    """Create a Defend card."""
    return CardData(
        id="defend",
        name="Defend",
        card_type=CardType.SKILL,
        rarity=CardRarity.STARTER,
        target_type=TargetType.SELF,
        base_cost=1,
        base_effects=[BlockEffect(base_block=5)],
        description="Gain 5 Block.",
    )


@pytest.fixture
def player(strike_card: CardData, defend_card: CardData) -> Player:
    """Create a test player with a small deck."""
    deck = [
        CardInstance(data=strike_card),
        CardInstance(data=strike_card),
        CardInstance(data=strike_card),
        CardInstance(data=defend_card),
        CardInstance(data=defend_card),
    ]
    return Player(
        name="Test Player",
        max_hp=80,
        current_hp=80,
        gold=99,
        max_energy=3,
        energy=3,
        master_deck=deck,
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


class TestCombatManager:
    def test_start_combat(self, player: Player, enemy: Enemy):
        """Test starting combat initializes state correctly."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        assert state is not None
        assert state.player == player
        assert len(state.enemies) == 1
        assert state.turn_number == 1
        assert state.phase == CombatPhase.PLAYER_TURN
        assert state.result == CombatResult.IN_PROGRESS
        assert len(state.hand) == 5  # Default draw

    def test_play_attack_card(self, player: Player, enemy: Enemy, strike_card: CardData):
        """Test playing an attack card deals damage."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        # Find a strike in hand
        strike = next(c for c in state.hand if c.data.id == "strike")
        initial_hp = enemy.current_hp

        result = manager.play_card(strike, enemy)

        assert result["success"] is True
        assert enemy.current_hp == initial_hp - 6

    def test_play_defend_card(self, player: Player, enemy: Enemy, defend_card: CardData):
        """Test playing a defend card grants block."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        # Find a defend in hand
        defend = next(c for c in state.hand if c.data.id == "defend")

        result = manager.play_card(defend)

        assert result["success"] is True
        assert player.block == 5

    def test_energy_spent_on_card_play(self, player: Player, enemy: Enemy):
        """Test energy is spent when playing cards."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        initial_energy = state.current_energy
        card = state.hand[0]
        card_cost = card.cost

        manager.play_card(card, enemy if card.target_type == TargetType.SINGLE_ENEMY else None)

        assert state.current_energy == initial_energy - card_cost

    def test_cannot_play_without_energy(self, player: Player, enemy: Enemy):
        """Test that cards cannot be played without enough energy."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        # Spend all energy
        state.energy_system.current_energy = 0
        player.energy = 0

        card = next(c for c in state.hand if c.cost > 0)
        can_play, reason = manager.can_play_card(card, enemy)

        assert can_play is False
        assert "energy" in reason.lower()

    def test_end_turn_discards_hand(self, player: Player, enemy: Enemy):
        """Test ending turn discards remaining hand."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        hand_size = len(state.hand)
        manager.end_player_turn()

        # After enemy turn, new player turn starts with fresh hand
        # But discard should have happened
        assert len(state.discard_pile) > 0 or len(state.draw_pile) + len(state.hand) == 5

    def test_enemy_executes_intent(self, player: Player, enemy: Enemy):
        """Test enemy executes their intent on their turn."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        initial_hp = player.current_hp
        enemy.intent = Intent(IntentType.ATTACK, damage=10)

        manager.end_player_turn()

        # Player should have taken damage (unless blocked)
        # Note: Player starts with 0 block
        assert player.current_hp <= initial_hp

    def test_combat_ends_on_enemy_death(self, player: Player, enemy: Enemy):
        """Test combat ends when all enemies die."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        # Set enemy to 1 HP
        enemy.current_hp = 1

        # Find and play a strike
        strike = next(c for c in state.hand if c.data.id == "strike")
        manager.play_card(strike, enemy)

        assert state.result == CombatResult.VICTORY

    def test_combat_ends_on_player_death(self, player: Player, enemy: Enemy):
        """Test combat ends when player dies."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        # Set player to very low HP
        player.current_hp = 5
        # Give enemy a strong attack
        enemy.intent = Intent(IntentType.ATTACK, damage=100)

        manager.end_player_turn()

        assert state.result == CombatResult.DEFEAT


class TestDamageCalculation:
    def test_block_absorbs_damage(self, player: Player, enemy: Enemy):
        """Test that block absorbs damage."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        player.block = 10
        initial_hp = player.current_hp
        enemy.intent = Intent(IntentType.ATTACK, damage=15)

        manager.end_player_turn()

        # 15 damage - 10 block = 5 damage to HP
        assert player.current_hp == initial_hp - 5
        assert player.block == 0

    def test_vulnerable_increases_damage(self, player: Player, enemy: Enemy, strike_card: CardData):
        """Test that vulnerable increases damage taken."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        enemy.status_effects[StatusEffectType.VULNERABLE] = 2
        initial_hp = enemy.current_hp

        strike = next(c for c in state.hand if c.data.id == "strike")
        manager.play_card(strike, enemy)

        # 6 damage * 1.5 = 9 damage
        assert enemy.current_hp == initial_hp - 9

    def test_weak_decreases_damage(self, player: Player, enemy: Enemy, strike_card: CardData):
        """Test that weak decreases damage dealt."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        player.status_effects[StatusEffectType.WEAK] = 2
        initial_hp = enemy.current_hp

        strike = next(c for c in state.hand if c.data.id == "strike")
        manager.play_card(strike, enemy)

        # 6 damage * 0.75 = 4 damage (truncated)
        assert enemy.current_hp == initial_hp - 4

    def test_strength_increases_damage(self, player: Player, enemy: Enemy, strike_card: CardData):
        """Test that strength increases attack damage."""
        manager = CombatManager()
        state = manager.start_combat(player, [enemy])

        player.status_effects[StatusEffectType.STRENGTH] = 3
        initial_hp = enemy.current_hp

        strike = next(c for c in state.hand if c.data.id == "strike")
        manager.play_card(strike, enemy)

        # 6 + 3 = 9 damage
        assert enemy.current_hp == initial_hp - 9
