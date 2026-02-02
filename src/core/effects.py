"""Effect system - the heart of card functionality."""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .enums import StatusEffectType, TargetType

if TYPE_CHECKING:
    from src.combat.combat_manager import CombatState
    from src.entities.enemy import Enemy
    from src.entities.player import Player


@dataclass
class Effect(ABC):
    """Base class for all effects in the game."""

    @abstractmethod
    def apply(
        self,
        combat_state: CombatState,
        source: Player | Enemy,
        target: Player | Enemy | list[Enemy] | None = None,
    ) -> dict[str, Any]:
        """
        Apply this effect to the target(s).

        Returns a dict with information about what happened for UI/logging.
        """
        pass

    @abstractmethod
    def get_description(self, upgraded: bool = False) -> str:
        """Return a human-readable description of this effect."""
        pass


@dataclass
class DamageEffect(Effect):
    """Deal damage to target(s)."""
    base_damage: int
    upgrade_amount: int = 0
    times: int = 1

    def apply(
        self,
        combat_state: CombatState,
        source: Player | Enemy,
        target: Player | Enemy | list[Enemy] | None = None,
    ) -> dict[str, Any]:
        from src.entities.player import Player

        results: dict[str, Any] = {"damage_dealt": [], "total_damage": 0}

        damage = self.base_damage

        # Apply strength if source has it
        if hasattr(source, "status_effects"):
            strength = source.status_effects.get(StatusEffectType.STRENGTH, 0)
            damage += strength

        # Handle multiple hits
        for _ in range(self.times):
            targets = [target] if not isinstance(target, list) else target

            for t in targets:
                if t is None:
                    continue

                actual_damage = damage

                # Check for vulnerable on target
                if hasattr(t, "status_effects"):
                    if t.status_effects.get(StatusEffectType.VULNERABLE, 0) > 0:
                        actual_damage = int(actual_damage * 1.5)

                # Check for weak on source
                if hasattr(source, "status_effects"):
                    if source.status_effects.get(StatusEffectType.WEAK, 0) > 0:
                        actual_damage = int(actual_damage * 0.75)

                # Apply block first
                blocked = min(t.block, actual_damage)
                t.block -= blocked
                remaining_damage = actual_damage - blocked

                # Then apply to HP
                t.current_hp -= remaining_damage
                t.current_hp = max(0, t.current_hp)

                results["damage_dealt"].append({
                    "target": t,
                    "damage": actual_damage,
                    "blocked": blocked,
                    "hp_lost": remaining_damage,
                })
                results["total_damage"] += actual_damage

        return results

    def get_description(self, upgraded: bool = False) -> str:
        damage = self.base_damage + (self.upgrade_amount if upgraded else 0)
        if self.times > 1:
            return f"Deal {damage} damage {self.times} times"
        return f"Deal {damage} damage"


@dataclass
class BlockEffect(Effect):
    """Gain block."""
    base_block: int
    upgrade_amount: int = 0

    def apply(
        self,
        combat_state: CombatState,
        source: Player | Enemy,
        target: Player | Enemy | list[Enemy] | None = None,
    ) -> dict[str, Any]:
        block = self.base_block

        # Apply dexterity if source has it
        if hasattr(source, "status_effects"):
            dexterity = source.status_effects.get(StatusEffectType.DEXTERITY, 0)
            block += dexterity

            # Check for frail
            if source.status_effects.get(StatusEffectType.FRAIL, 0) > 0:
                block = int(block * 0.75)

        # Target defaults to source for block
        actual_target = target if target else source
        if isinstance(actual_target, list):
            actual_target = source

        actual_target.block += block

        return {"block_gained": block, "target": actual_target}

    def get_description(self, upgraded: bool = False) -> str:
        block = self.base_block + (self.upgrade_amount if upgraded else 0)
        return f"Gain {block} Block"


@dataclass
class DrawEffect(Effect):
    """Draw cards from the draw pile."""
    cards: int
    upgrade_amount: int = 0

    def apply(
        self,
        combat_state: CombatState,
        source: Player | Enemy,
        target: Player | Enemy | list[Enemy] | None = None,
    ) -> dict[str, Any]:
        drawn = combat_state.deck_manager.draw(self.cards)
        return {"cards_drawn": drawn, "count": len(drawn)}

    def get_description(self, upgraded: bool = False) -> str:
        cards = self.cards + (self.upgrade_amount if upgraded else 0)
        if cards == 1:
            return "Draw 1 card"
        return f"Draw {cards} cards"


@dataclass
class ApplyStatusEffect(Effect):
    """Apply a status effect to target(s)."""
    status_type: StatusEffectType
    amount: int
    upgrade_amount: int = 0

    def apply(
        self,
        combat_state: CombatState,
        source: Player | Enemy,
        target: Player | Enemy | list[Enemy] | None = None,
    ) -> dict[str, Any]:
        results: dict[str, Any] = {"effects_applied": []}

        targets = [target] if not isinstance(target, list) else target

        for t in targets:
            if t is None:
                continue

            # Check for artifact (blocks debuffs)
            if hasattr(t, "status_effects"):
                if self._is_debuff() and t.status_effects.get(StatusEffectType.ARTIFACT, 0) > 0:
                    t.status_effects[StatusEffectType.ARTIFACT] -= 1
                    if t.status_effects[StatusEffectType.ARTIFACT] <= 0:
                        del t.status_effects[StatusEffectType.ARTIFACT]
                    results["effects_applied"].append({
                        "target": t,
                        "status": self.status_type,
                        "blocked_by_artifact": True,
                    })
                    continue

                current = t.status_effects.get(self.status_type, 0)
                t.status_effects[self.status_type] = current + self.amount

                results["effects_applied"].append({
                    "target": t,
                    "status": self.status_type,
                    "amount": self.amount,
                    "new_total": t.status_effects[self.status_type],
                })

        return results

    def _is_debuff(self) -> bool:
        """Check if this status effect is a debuff."""
        debuffs = {
            StatusEffectType.VULNERABLE,
            StatusEffectType.WEAK,
            StatusEffectType.FRAIL,
            StatusEffectType.POISON,
        }
        return self.status_type in debuffs

    def get_description(self, upgraded: bool = False) -> str:
        amount = self.amount + (self.upgrade_amount if upgraded else 0)
        name = self.status_type.name.replace("_", " ").title()
        return f"Apply {amount} {name}"


@dataclass
class GainEnergyEffect(Effect):
    """Gain energy this turn."""
    amount: int
    upgrade_amount: int = 0

    def apply(
        self,
        combat_state: CombatState,
        source: Player | Enemy,
        target: Player | Enemy | list[Enemy] | None = None,
    ) -> dict[str, Any]:
        from src.entities.player import Player

        if isinstance(source, Player):
            source.energy += self.amount
            return {"energy_gained": self.amount}
        return {"energy_gained": 0}

    def get_description(self, upgraded: bool = False) -> str:
        amount = self.amount + (self.upgrade_amount if upgraded else 0)
        return f"Gain {amount} Energy"


@dataclass
class HealEffect(Effect):
    """Heal HP."""
    amount: int
    upgrade_amount: int = 0

    def apply(
        self,
        combat_state: CombatState,
        source: Player | Enemy,
        target: Player | Enemy | list[Enemy] | None = None,
    ) -> dict[str, Any]:
        actual_target = target if target else source
        if isinstance(actual_target, list):
            actual_target = source

        old_hp = actual_target.current_hp
        actual_target.current_hp = min(
            actual_target.max_hp,
            actual_target.current_hp + self.amount
        )
        healed = actual_target.current_hp - old_hp

        return {"healed": healed, "target": actual_target}

    def get_description(self, upgraded: bool = False) -> str:
        amount = self.amount + (self.upgrade_amount if upgraded else 0)
        return f"Heal {amount} HP"


@dataclass
class ExhaustEffect(Effect):
    """Exhaust cards from hand."""
    count: int = 1
    random: bool = False

    def apply(
        self,
        combat_state: CombatState,
        source: Player | Enemy,
        target: Player | Enemy | list[Enemy] | None = None,
    ) -> dict[str, Any]:
        # This would need UI interaction for non-random exhaust
        # For now, just mark that exhaust should happen
        return {"exhaust_count": self.count, "random": self.random}

    def get_description(self, upgraded: bool = False) -> str:
        if self.random:
            return f"Exhaust {self.count} random card(s)"
        return f"Exhaust {self.count} card(s)"


@dataclass
class CompositeEffect(Effect):
    """Combines multiple effects into one."""
    effects: list[Effect] = field(default_factory=list)

    def apply(
        self,
        combat_state: CombatState,
        source: Player | Enemy,
        target: Player | Enemy | list[Enemy] | None = None,
    ) -> dict[str, Any]:
        results: dict[str, Any] = {"sub_effects": []}
        for effect in self.effects:
            result = effect.apply(combat_state, source, target)
            results["sub_effects"].append(result)
        return results

    def get_description(self, upgraded: bool = False) -> str:
        return ". ".join(e.get_description(upgraded) for e in self.effects)
