"""Tests for map generation."""

import pytest
from src.core.enums import MapNodeType
from src.map.map_node import MapNode
from src.map.map_generator import MapGenerator, MapConfig, GameMap


class TestMapNode:
    def test_node_creation(self):
        """Test creating a map node."""
        node = MapNode(
            node_type=MapNodeType.COMBAT,
            row=0,
            col=2,
        )

        assert node.node_type == MapNodeType.COMBAT
        assert node.row == 0
        assert node.col == 2
        assert not node.visited
        assert not node.available

    def test_add_connection(self):
        """Test adding connections between nodes."""
        node1 = MapNode(node_type=MapNodeType.COMBAT, row=0, col=0)
        node2 = MapNode(node_type=MapNodeType.COMBAT, row=1, col=0)

        node1.add_connection(node2)

        assert node2 in node1.connections
        assert len(node1.connections) == 1

    def test_no_duplicate_connections(self):
        """Test that duplicate connections are not added."""
        node1 = MapNode(node_type=MapNodeType.COMBAT, row=0, col=0)
        node2 = MapNode(node_type=MapNodeType.COMBAT, row=1, col=0)

        node1.add_connection(node2)
        node1.add_connection(node2)

        assert len(node1.connections) == 1

    def test_node_symbols(self):
        """Test node type symbols."""
        combat = MapNode(node_type=MapNodeType.COMBAT, row=0, col=0)
        elite = MapNode(node_type=MapNodeType.ELITE, row=0, col=0)
        rest = MapNode(node_type=MapNodeType.REST, row=0, col=0)
        shop = MapNode(node_type=MapNodeType.SHOP, row=0, col=0)
        event = MapNode(node_type=MapNodeType.EVENT, row=0, col=0)

        assert combat.get_ascii_symbol() == "M"
        assert elite.get_ascii_symbol() == "E"
        assert rest.get_ascii_symbol() == "R"
        assert shop.get_ascii_symbol() == "$"
        assert event.get_ascii_symbol() == "?"


class TestMapGenerator:
    def test_generate_map(self):
        """Test basic map generation."""
        generator = MapGenerator()
        game_map = generator.generate(act=1, seed=42)

        assert game_map is not None
        assert len(game_map.nodes) > 0
        assert game_map.boss_node is not None

    def test_deterministic_with_seed(self):
        """Test that same seed produces same map."""
        generator = MapGenerator()
        map1 = generator.generate(act=1, seed=12345)
        map2 = generator.generate(act=1, seed=12345)

        # Same number of nodes in each row
        assert len(map1.nodes) == len(map2.nodes)
        for row1, row2 in zip(map1.nodes, map2.nodes):
            assert len(row1) == len(row2)

    def test_all_nodes_connected(self):
        """Test that all nodes have paths to them."""
        generator = MapGenerator()
        game_map = generator.generate(act=1, seed=42)

        # Check each row (except first) has incoming connections
        for row_idx in range(1, len(game_map.nodes)):
            for node in game_map.nodes[row_idx]:
                # Find nodes in previous row that connect to this one
                incoming = [
                    n for n in game_map.nodes[row_idx - 1]
                    if node in n.connections
                ]
                assert len(incoming) > 0, f"Node at row {row_idx} has no incoming connections"

    def test_first_row_available(self):
        """Test that first row nodes are initially available."""
        generator = MapGenerator()
        game_map = generator.generate(act=1, seed=42)

        for node in game_map.nodes[0]:
            assert node.available

    def test_boss_node_connected(self):
        """Test that boss node is connected from last row."""
        generator = MapGenerator()
        game_map = generator.generate(act=1, seed=42)

        last_row = game_map.nodes[-1]
        for node in last_row:
            assert game_map.boss_node in node.connections


class TestGameMap:
    def test_get_available_nodes(self):
        """Test getting available nodes."""
        generator = MapGenerator()
        game_map = generator.generate(act=1, seed=42)

        # Initially, first row is available
        available = game_map.get_available_nodes()
        assert len(available) > 0
        assert all(node.row == 0 for node in available)

    def test_move_to_node(self):
        """Test moving to a node."""
        generator = MapGenerator()
        game_map = generator.generate(act=1, seed=42)

        first_node = game_map.get_available_nodes()[0]
        result = game_map.move_to_node(first_node)

        assert result is True
        assert first_node.visited
        assert game_map.current_node == first_node
        assert game_map.current_row == 0

    def test_move_updates_availability(self):
        """Test that moving updates available nodes."""
        generator = MapGenerator()
        game_map = generator.generate(act=1, seed=42)

        first_node = game_map.get_available_nodes()[0]
        game_map.move_to_node(first_node)

        # Now available nodes should be from connections
        available = game_map.get_available_nodes()
        assert all(node in first_node.connections for node in available)

    def test_cannot_move_to_unavailable(self):
        """Test that you cannot move to unavailable nodes."""
        generator = MapGenerator()
        game_map = generator.generate(act=1, seed=42)

        # Try to move to a node not in first row
        if len(game_map.nodes) > 1:
            unavailable_node = game_map.nodes[1][0]
            result = game_map.move_to_node(unavailable_node)
            assert result is False

    def test_is_complete(self):
        """Test checking if map is complete."""
        generator = MapGenerator()
        game_map = generator.generate(act=1, seed=42)

        assert not game_map.is_complete()

        # Mark boss as visited
        if game_map.boss_node:
            game_map.boss_node.visited = True
            assert game_map.is_complete()

    def test_render_ascii(self):
        """Test ASCII map rendering."""
        generator = MapGenerator()
        game_map = generator.generate(act=1, seed=42)

        ascii_map = game_map.render_ascii()

        assert len(ascii_map) > 0
        assert "START" in ascii_map
        assert "[B]" in ascii_map  # Boss
