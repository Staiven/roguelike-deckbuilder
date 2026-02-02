"""Procedural map generation."""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.core.enums import MapNodeType
from src.map.map_node import MapNode

if TYPE_CHECKING:
    pass


@dataclass
class MapConfig:
    """Configuration for map generation."""
    num_rows: int = 15
    min_paths: int = 2
    max_paths: int = 4
    path_density: float = 0.5  # Chance of path continuing at each row

    # Node type weights by row (early, mid, late)
    early_weights: dict[MapNodeType, float] = field(default_factory=lambda: {
        MapNodeType.COMBAT: 0.6,
        MapNodeType.EVENT: 0.25,
        MapNodeType.SHOP: 0.05,
        MapNodeType.REST: 0.05,
        MapNodeType.ELITE: 0.05,
    })

    mid_weights: dict[MapNodeType, float] = field(default_factory=lambda: {
        MapNodeType.COMBAT: 0.45,
        MapNodeType.EVENT: 0.2,
        MapNodeType.SHOP: 0.1,
        MapNodeType.REST: 0.1,
        MapNodeType.ELITE: 0.15,
    })

    late_weights: dict[MapNodeType, float] = field(default_factory=lambda: {
        MapNodeType.COMBAT: 0.35,
        MapNodeType.EVENT: 0.15,
        MapNodeType.SHOP: 0.1,
        MapNodeType.REST: 0.2,
        MapNodeType.ELITE: 0.2,
    })

    # Guaranteed nodes
    guaranteed_rest_before_boss: bool = True
    guaranteed_elite_rows: list[int] = field(default_factory=lambda: [6, 12])
    guaranteed_treasure_row: int | None = None  # Row 0 for treasure chest


@dataclass
class GameMap:
    """
    A complete map for one act.

    Contains all nodes and tracks the player's progress.
    """
    nodes: list[list[MapNode]] = field(default_factory=list)
    current_row: int = -1
    current_node: MapNode | None = None
    boss_node: MapNode | None = None

    def get_row(self, row_index: int) -> list[MapNode]:
        """Get all nodes in a specific row."""
        if 0 <= row_index < len(self.nodes):
            return self.nodes[row_index]
        return []

    def get_available_nodes(self) -> list[MapNode]:
        """Get nodes the player can currently move to."""
        if self.current_row == -1:
            # At start, first row is available
            return self.nodes[0] if self.nodes else []

        available: list[MapNode] = []
        if self.current_node:
            for node in self.current_node.connections:
                available.append(node)
        return available

    def move_to_node(self, node: MapNode) -> bool:
        """
        Move the player to a node.

        Returns True if successful.
        """
        available = self.get_available_nodes()
        if node not in available:
            return False

        # Mark old position
        if self.current_node:
            self.current_node.available = False

        # Move to new node
        self.current_node = node
        self.current_row = node.row
        node.visited = True

        # Update availability for connected nodes
        for n in self.nodes[self.current_row]:
            n.available = False
        for connected in node.connections:
            connected.available = True

        return True

    def is_complete(self) -> bool:
        """Check if the map has been completed (boss defeated)."""
        return self.boss_node is not None and self.boss_node.visited

    def render_ascii(self) -> str:
        """Render the map as ASCII art."""
        if not self.nodes:
            return "Empty map"

        lines: list[str] = []

        # Render boss at top
        if self.boss_node:
            lines.append("        [B]")
            lines.append("         |")

        # Render rows from top to bottom
        for row_idx in range(len(self.nodes) - 1, -1, -1):
            row = self.nodes[row_idx]

            # Build node line
            node_chars: list[str] = []
            for col in range(7):  # Max 7 columns
                node = next((n for n in row if n.col == col), None)
                if node:
                    if node == self.current_node:
                        node_chars.append(f"[{node.get_ascii_symbol()}]")
                    elif node.visited:
                        node_chars.append(f"({node.get_ascii_symbol()})")
                    elif node.available:
                        node_chars.append(f"<{node.get_ascii_symbol()}>")
                    else:
                        node_chars.append(f" {node.get_ascii_symbol()} ")
                else:
                    node_chars.append("   ")

            lines.append(" ".join(node_chars))

            # Render connections (simplified)
            if row_idx > 0:
                lines.append("   " + "  |  " * min(len(row), 3))

        # Starting position indicator
        lines.append("        ▲")
        lines.append("      START")

        return "\n".join(lines)


class MapGenerator:
    """Generates procedural maps for each act."""

    def __init__(self, config: MapConfig | None = None):
        self.config = config or MapConfig()

    def generate(self, act: int = 1, seed: int | None = None) -> GameMap:
        """
        Generate a new map for the given act.

        Args:
            act: Act number (affects difficulty and node distribution)
            seed: Random seed for reproducible generation

        Returns:
            A complete GameMap
        """
        if seed is not None:
            random.seed(seed)

        game_map = GameMap()

        # Generate the node grid
        nodes_by_row: list[list[MapNode]] = []

        for row in range(self.config.num_rows):
            row_nodes = self._generate_row(row, act)
            nodes_by_row.append(row_nodes)

        game_map.nodes = nodes_by_row

        # Generate connections between rows
        self._generate_connections(game_map)

        # Add boss node
        boss = MapNode(
            node_type=MapNodeType.BOSS,
            row=self.config.num_rows,
            col=3,
        )
        game_map.boss_node = boss

        # Connect last row to boss
        for node in nodes_by_row[-1]:
            node.add_connection(boss)

        # Add guaranteed rest before boss if configured
        if self.config.guaranteed_rest_before_boss:
            last_row = nodes_by_row[-1]
            # Ensure at least one rest site
            if not any(n.node_type == MapNodeType.REST for n in last_row):
                if last_row:
                    last_row[0].node_type = MapNodeType.REST

        # Set initial availability
        for node in nodes_by_row[0]:
            node.available = True

        return game_map

    def _generate_row(self, row: int, act: int) -> list[MapNode]:
        """Generate nodes for a single row."""
        # Determine number of nodes in this row
        if row == 0:
            num_nodes = random.randint(2, 3)
        elif row == self.config.num_rows - 1:
            num_nodes = random.randint(1, 2)
        else:
            num_nodes = random.randint(self.config.min_paths, self.config.max_paths)

        # Generate column positions
        max_cols = 7
        positions = random.sample(range(max_cols), min(num_nodes, max_cols))
        positions.sort()

        nodes: list[MapNode] = []

        for col in positions:
            node_type = self._choose_node_type(row, act)

            # Check for guaranteed elite rows
            if row in self.config.guaranteed_elite_rows:
                if random.random() < 0.5:
                    node_type = MapNodeType.ELITE

            node = MapNode(
                node_type=node_type,
                row=row,
                col=col,
                x=col * 1.0 + random.uniform(-0.2, 0.2),
                y=row * 1.0,
            )
            nodes.append(node)

        return nodes

    def _choose_node_type(self, row: int, act: int) -> MapNodeType:
        """Choose a node type based on row position and act."""
        # Determine which weight set to use
        early_threshold = self.config.num_rows // 3
        mid_threshold = 2 * self.config.num_rows // 3

        if row < early_threshold:
            weights = self.config.early_weights
        elif row < mid_threshold:
            weights = self.config.mid_weights
        else:
            weights = self.config.late_weights

        # Weighted random selection
        types = list(weights.keys())
        probs = list(weights.values())

        return random.choices(types, weights=probs, k=1)[0]

    def _generate_connections(self, game_map: GameMap) -> None:
        """Generate connections between rows."""
        nodes_by_row = game_map.nodes

        for row_idx in range(len(nodes_by_row) - 1):
            current_row = nodes_by_row[row_idx]
            next_row = nodes_by_row[row_idx + 1]

            if not current_row or not next_row:
                continue

            # Ensure each node connects to at least one node in the next row
            for node in current_row:
                # Find valid connections (nearby columns)
                valid_targets = [
                    n for n in next_row
                    if abs(n.col - node.col) <= 2
                ]

                if not valid_targets:
                    # If no nearby nodes, connect to closest
                    valid_targets = sorted(next_row, key=lambda n: abs(n.col - node.col))[:1]

                # Connect to 1-2 nodes
                num_connections = min(random.randint(1, 2), len(valid_targets))
                targets = random.sample(valid_targets, num_connections)

                for target in targets:
                    node.add_connection(target)

            # Ensure each node in next row is reachable from at least one node
            for node in next_row:
                incoming = [n for n in current_row if node in n.connections]
                if not incoming:
                    # Connect from closest node in previous row
                    closest = min(current_row, key=lambda n: abs(n.col - node.col))
                    closest.add_connection(node)
