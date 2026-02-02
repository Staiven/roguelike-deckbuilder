"""Enemy base class and intent system."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable, Any
import random

from src.core.enums import StatusEffectType, IntentType

if TYPE_CHECKING:
    from src.combat.combat_manager import CombatState


@dataclass
class Intent:
    """Represents an enemy's next action, shown to the player."""
    intent_type: IntentType
    damage: int | None = None
    times: int = 1
    block: int | None = None
    buff_amount: int | None = None
    debuff_amount: int | None = None

    def get_display_string(self) -> str:
        """Get a string representation for display."""
        parts = []

        if self.damage is not None:
            if self.times > 1:
                parts.append(f"{self.damage}x{self.times}")
            else:
                parts.append(str(self.damage))

        if self.block is not None:
            parts.append(f"Block {self.block}")

        if parts:
            return " | ".join(parts)

        return self.intent_type.name.replace("_", " ").title()


# Type for enemy AI functions
EnemyAI = Callable[["Enemy", "CombatState"], Intent]


@dataclass
class EnemyData:
    """
    Immutable enemy definition template.

    This is the base data for an enemy type. Enemy instances wrap this
    with runtime state.
    """
    id: str
    name: str
    max_hp_range: tuple[int, int]
    ai_function: EnemyAI | None = None


@dataclass
class Enemy:
    """
    An enemy instance in combat.

    Contains both the base data and runtime state.
    """
    id: str
    name: str
    max_hp: int
    current_hp: int
    block: int = 0
    status_effects: dict[StatusEffectType, int] = field(default_factory=dict)
    intent: Intent = field(default_factory=lambda: Intent(IntentType.UNKNOWN))
    ai_function: EnemyAI | None = None

    # Combat state
    move_history: list[str] = field(default_factory=list)
    turn_count: int = 0

    @classmethod
    def from_data(cls, data: EnemyData, ascension: int = 0) -> Enemy:
        """Create an Enemy instance from EnemyData."""
        min_hp, max_hp = data.max_hp_range
        hp = random.randint(min_hp, max_hp)

        # Ascension can increase enemy HP
        if ascension >= 7:
            hp = int(hp * 1.1)

        return cls(
            id=data.id,
            name=data.name,
            max_hp=hp,
            current_hp=hp,
            ai_function=data.ai_function,
        )

    def is_alive(self) -> bool:
        """Check if the enemy is still alive."""
        return self.current_hp > 0

    def take_damage(self, amount: int, piercing: bool = False) -> int:
        """
        Deal damage to the enemy.

        Args:
            amount: Raw damage amount
            piercing: If True, ignores block

        Returns:
            Actual HP lost
        """
        if amount <= 0:
            return 0

        if piercing:
            blocked = 0
            remaining = amount
        else:
            blocked = min(self.block, amount)
            self.block -= blocked
            remaining = amount - blocked

        self.current_hp -= remaining
        self.current_hp = max(0, self.current_hp)

        return remaining

    def gain_block(self, amount: int) -> int:
        """Gain block."""
        if amount <= 0:
            return 0
        self.block += amount
        return amount

    def heal(self, amount: int) -> int:
        """Heal the enemy."""
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp

    def choose_intent(self, combat_state: CombatState) -> Intent:
        """
        Choose the next action based on AI.

        This should be called at the start of each turn to determine
        what the enemy will do.
        """
        if self.ai_function:
            self.intent = self.ai_function(self, combat_state)
        else:
            # Default behavior: alternate between attack and defend
            if self.turn_count % 2 == 0:
                self.intent = Intent(IntentType.ATTACK, damage=6)
            else:
                self.intent = Intent(IntentType.DEFEND, block=5)

        return self.intent

    def execute_intent(self, combat_state: CombatState) -> dict[str, Any]:
        """
        Execute the current intent.

        Returns a dict with information about what happened.
        """
        result: dict[str, Any] = {"intent": self.intent}
        player = combat_state.player

        # Calculate actual damage with status effects
        if self.intent.damage is not None:
            damage = self.intent.damage

            # Apply strength
            strength = self.status_effects.get(StatusEffectType.STRENGTH, 0)
            damage += strength

            # Apply weak
            if self.status_effects.get(StatusEffectType.WEAK, 0) > 0:
                damage = int(damage * 0.75)

            # Check for vulnerable on player
            if player.status_effects.get(StatusEffectType.VULNERABLE, 0) > 0:
                damage = int(damage * 1.5)

            damage = max(0, damage)

            # Deal damage (possibly multiple times)
            total_damage = 0
            for _ in range(self.intent.times):
                hp_lost = player.take_damage(damage)
                total_damage += hp_lost

            result["damage_dealt"] = total_damage

        # Gain block
        if self.intent.block is not None:
            self.gain_block(self.intent.block)
            result["block_gained"] = self.intent.block

        self.move_history.append(self.intent.intent_type.name)
        self.turn_count += 1

        return result

    def start_turn(self) -> None:
        """Called at the start of each enemy turn."""
        self.block = 0

    def end_turn(self) -> None:
        """Called at the end of each enemy turn."""
        # Decrement status effect durations
        for effect_type in [StatusEffectType.VULNERABLE, StatusEffectType.WEAK]:
            if effect_type in self.status_effects:
                self.status_effects[effect_type] -= 1
                if self.status_effects[effect_type] <= 0:
                    del self.status_effects[effect_type]

        # Apply poison damage
        poison = self.status_effects.get(StatusEffectType.POISON, 0)
        if poison > 0:
            self.current_hp -= poison
            self.current_hp = max(0, self.current_hp)
            self.status_effects[StatusEffectType.POISON] = poison - 1
            if self.status_effects[StatusEffectType.POISON] <= 0:
                del self.status_effects[StatusEffectType.POISON]

    def __str__(self) -> str:
        status_str = ""
        if self.status_effects:
            effects = [f"{k.name}:{v}" for k, v in self.status_effects.items()]
            status_str = f" [{', '.join(effects)}]"
        return f"{self.name} (HP: {self.current_hp}/{self.max_hp}, Block: {self.block}){status_str}"
