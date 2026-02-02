"""Energy management system."""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.player import Player


@dataclass
class EnergySystem:
    """
    Manages energy during combat.

    Energy is the resource spent to play cards. It refreshes each turn.
    """
    current_energy: int = 0
    max_energy: int = 3
    bonus_energy_next_turn: int = 0

    def initialize(self, player: Player) -> None:
        """Initialize energy at the start of combat."""
        self.max_energy = player.max_energy
        self.current_energy = self.max_energy
        self.bonus_energy_next_turn = 0

    def start_turn(self) -> int:
        """
        Refresh energy at the start of turn.

        Returns the energy available this turn.
        """
        self.current_energy = self.max_energy + self.bonus_energy_next_turn
        self.bonus_energy_next_turn = 0
        return self.current_energy

    def end_turn(self) -> int:
        """
        Handle end of turn energy.

        Returns unspent energy (for relics that care about this).
        """
        unspent = self.current_energy
        # Note: Some relics/powers may want to preserve energy
        # That would be handled through status effects or relic triggers
        return unspent

    def can_spend(self, amount: int) -> bool:
        """Check if we have enough energy to spend."""
        return self.current_energy >= amount

    def spend(self, amount: int) -> bool:
        """
        Spend energy.

        Returns True if successful, False if insufficient energy.
        """
        if amount < 0:
            return False

        if self.current_energy >= amount:
            self.current_energy -= amount
            return True
        return False

    def gain(self, amount: int) -> int:
        """
        Gain energy this turn.

        Returns the new current energy.
        """
        self.current_energy += amount
        return self.current_energy

    def gain_next_turn(self, amount: int) -> None:
        """Add bonus energy for the next turn."""
        self.bonus_energy_next_turn += amount

    def gain_max_energy(self, amount: int = 1) -> None:
        """Permanently increase max energy."""
        self.max_energy += amount

    def lose_max_energy(self, amount: int = 1) -> None:
        """Permanently decrease max energy."""
        self.max_energy = max(0, self.max_energy - amount)

    def set_energy(self, amount: int) -> None:
        """Set current energy to a specific value."""
        self.current_energy = max(0, amount)

    def __str__(self) -> str:
        return f"Energy: {self.current_energy}/{self.max_energy}"
