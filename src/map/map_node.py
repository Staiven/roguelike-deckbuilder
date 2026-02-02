"""Map node types and data structures."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.core.enums import MapNodeType

if TYPE_CHECKING:
    pass


@dataclass
class MapNode:
    """
    A single node on the map.

    Nodes represent encounters, rest sites, shops, etc. that the player
    can visit during their run.
    """
    node_type: MapNodeType
    row: int
    col: int
    x: float = 0.0  # For rendering (can be offset for visual variety)
    y: float = 0.0
    connections: list[MapNode] = field(default_factory=list)
    visited: bool = False
    available: bool = False  # Can the player move here currently?

    # Node-specific data
    enemy_pool: str | None = None  # Which enemy pool to draw from
    is_burning: bool = False  # For rest sites that have been "burned"

    def add_connection(self, node: MapNode) -> None:
        """Add a connection to another node."""
        if node not in self.connections:
            self.connections.append(node)

    def get_symbol(self) -> str:
        """Get a text symbol for this node type."""
        symbols = {
            MapNodeType.COMBAT: "⚔",
            MapNodeType.ELITE: "☠",
            MapNodeType.REST: "🔥",
            MapNodeType.SHOP: "💰",
            MapNodeType.EVENT: "?",
            MapNodeType.BOSS: "👹",
            MapNodeType.TREASURE: "💎",
        }
        return symbols.get(self.node_type, "?")

    def get_ascii_symbol(self) -> str:
        """Get an ASCII symbol for this node type."""
        symbols = {
            MapNodeType.COMBAT: "M",   # Monster
            MapNodeType.ELITE: "E",    # Elite
            MapNodeType.REST: "R",     # Rest
            MapNodeType.SHOP: "$",     # Shop
            MapNodeType.EVENT: "?",    # Event/Unknown
            MapNodeType.BOSS: "B",     # Boss
            MapNodeType.TREASURE: "T", # Treasure
        }
        return symbols.get(self.node_type, "?")

    def __str__(self) -> str:
        status = "✓" if self.visited else ("→" if self.available else " ")
        return f"[{status}] {self.get_ascii_symbol()} ({self.row},{self.col})"

    def __repr__(self) -> str:
        return f"MapNode({self.node_type.name}, row={self.row}, col={self.col})"

    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MapNode):
            return NotImplemented
        return self.row == other.row and self.col == other.col
