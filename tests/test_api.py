"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app, sessions
from src.core.events import reset_event_bus


@pytest.fixture(autouse=True)
def reset_state():
    """Reset state before each test."""
    sessions.clear()
    reset_event_bus()
    yield
    sessions.clear()
    reset_event_bus()


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestCreateGame:
    """Test game creation endpoints."""

    def test_create_warrior_game(self, client):
        response = client.post(
            "/api/game/new",
            json={"character_class": "warrior"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "game_state" in data
        assert data["game_state"]["player"]["name"] == "Ironclad"

    def test_create_mage_game(self, client):
        response = client.post(
            "/api/game/new",
            json={"character_class": "mage"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["game_state"]["player"]["name"] == "Silent"

    def test_create_game_with_seed(self, client):
        response1 = client.post(
            "/api/game/new",
            json={"character_class": "warrior", "seed": 12345}
        )
        response2 = client.post(
            "/api/game/new",
            json={"character_class": "warrior", "seed": 12345}
        )
        # Same seed should produce same map layout
        map1 = response1.json()["game_state"]["map"]
        map2 = response2.json()["game_state"]["map"]
        assert map1["nodes"][0][0]["node_type"] == map2["nodes"][0][0]["node_type"]

    def test_create_game_invalid_class(self, client):
        response = client.post(
            "/api/game/new",
            json={"character_class": "invalid"}
        )
        assert response.status_code == 400
        assert "Invalid character class" in response.json()["detail"]


class TestGetGameState:
    """Test game state retrieval."""

    def test_get_state(self, client):
        # Create a game first
        create_response = client.post(
            "/api/game/new",
            json={"character_class": "warrior"}
        )
        session_id = create_response.json()["session_id"]

        # Get state
        response = client.get(f"/api/game/{session_id}/state")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "player" in data
        assert "map" in data

    def test_get_state_invalid_session(self, client):
        response = client.get("/api/game/invalid-session-id/state")
        assert response.status_code == 404


class TestMapMovement:
    """Test map movement endpoints."""

    def test_move_to_valid_node(self, client):
        # Create a game
        create_response = client.post(
            "/api/game/new",
            json={"character_class": "warrior"}
        )
        session_id = create_response.json()["session_id"]
        game_state = create_response.json()["game_state"]

        # Find an available node
        available_node = None
        for row in game_state["map"]["nodes"]:
            for node in row:
                if node["available"]:
                    available_node = node
                    break
            if available_node:
                break

        assert available_node is not None

        # Move to it
        response = client.post(
            f"/api/game/{session_id}/move",
            json={"row": available_node["row"], "col": available_node["col"]}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_move_to_invalid_node(self, client):
        # Create a game
        create_response = client.post(
            "/api/game/new",
            json={"character_class": "warrior"}
        )
        session_id = create_response.json()["session_id"]

        # Try to move to non-existent node
        response = client.post(
            f"/api/game/{session_id}/move",
            json={"row": 99, "col": 99}
        )
        assert response.status_code == 400


class TestCombat:
    """Test combat endpoints."""

    def _enter_combat(self, client) -> tuple[str, dict]:
        """Helper to create a game and enter combat."""
        create_response = client.post(
            "/api/game/new",
            json={"character_class": "warrior", "seed": 42}
        )
        session_id = create_response.json()["session_id"]
        game_state = create_response.json()["game_state"]

        # Find a combat node (MONSTER type)
        combat_node = None
        for row in game_state["map"]["nodes"]:
            for node in row:
                if node["available"] and node["node_type"] == "MONSTER":
                    combat_node = node
                    break
            if combat_node:
                break

        if combat_node is None:
            # If no monster, just take first available
            for row in game_state["map"]["nodes"]:
                for node in row:
                    if node["available"]:
                        combat_node = node
                        break
                if combat_node:
                    break

        # Move to combat node
        move_response = client.post(
            f"/api/game/{session_id}/move",
            json={"row": combat_node["row"], "col": combat_node["col"]}
        )
        return session_id, move_response.json()["game_state"]

    def test_play_card(self, client):
        session_id, game_state = self._enter_combat(client)

        # Skip if not in combat
        if game_state["state"] != "COMBAT":
            pytest.skip("Did not enter combat")

        combat = game_state["combat"]
        assert combat is not None
        assert len(combat["hand"]) > 0

        # Find an attack card that targets single enemy
        card_index = None
        for i, card in enumerate(combat["hand"]):
            if card["target_type"] == "SINGLE_ENEMY" and card["cost"] <= combat["current_energy"]:
                card_index = i
                break

        if card_index is None:
            pytest.skip("No playable single-target card in hand")

        # Play the card
        response = client.post(
            f"/api/game/{session_id}/combat/play-card",
            json={"card_index": card_index, "target_index": 0}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_play_card_invalid_index(self, client):
        session_id, game_state = self._enter_combat(client)

        if game_state["state"] != "COMBAT":
            pytest.skip("Did not enter combat")

        response = client.post(
            f"/api/game/{session_id}/combat/play-card",
            json={"card_index": 999, "target_index": 0}
        )
        assert response.status_code == 400

    def test_end_turn(self, client):
        session_id, game_state = self._enter_combat(client)

        if game_state["state"] != "COMBAT":
            pytest.skip("Did not enter combat")

        initial_turn = game_state["combat"]["turn_number"]

        response = client.post(f"/api/game/{session_id}/combat/end-turn")
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Turn should have advanced (if combat didn't end)
        new_state = response.json()["game_state"]
        if new_state["state"] == "COMBAT":
            assert new_state["combat"]["turn_number"] == initial_turn + 1

    def test_end_turn_not_in_combat(self, client):
        create_response = client.post(
            "/api/game/new",
            json={"character_class": "warrior"}
        )
        session_id = create_response.json()["session_id"]

        response = client.post(f"/api/game/{session_id}/combat/end-turn")
        assert response.status_code == 400
        assert "Not in combat" in response.json()["detail"]


class TestRewards:
    """Test reward endpoints."""

    def test_skip_reward_not_in_reward_state(self, client):
        create_response = client.post(
            "/api/game/new",
            json={"character_class": "warrior"}
        )
        session_id = create_response.json()["session_id"]

        response = client.post(f"/api/game/{session_id}/reward/skip")
        assert response.status_code == 400


class TestGameStateResponse:
    """Test that game state responses have correct structure."""

    def test_game_state_has_required_fields(self, client):
        response = client.post(
            "/api/game/new",
            json={"character_class": "warrior"}
        )
        game_state = response.json()["game_state"]

        # Check top-level fields
        assert "session_id" in game_state
        assert "state" in game_state
        assert "act" in game_state
        assert "floor" in game_state
        assert "player" in game_state
        assert "map" in game_state
        assert "deck" in game_state

    def test_player_response_has_required_fields(self, client):
        response = client.post(
            "/api/game/new",
            json={"character_class": "warrior"}
        )
        player = response.json()["game_state"]["player"]

        assert "name" in player
        assert "max_hp" in player
        assert "current_hp" in player
        assert "gold" in player
        assert "energy" in player
        assert "block" in player
        assert "deck_size" in player
        assert "relics" in player

    def test_map_response_has_required_fields(self, client):
        response = client.post(
            "/api/game/new",
            json={"character_class": "warrior"}
        )
        map_data = response.json()["game_state"]["map"]

        assert "nodes" in map_data
        assert "current_row" in map_data
        assert len(map_data["nodes"]) > 0

    def test_card_response_has_required_fields(self, client):
        response = client.post(
            "/api/game/new",
            json={"character_class": "warrior"}
        )
        deck = response.json()["game_state"]["deck"]

        assert len(deck) > 0
        card = deck[0]

        assert "id" in card
        assert "name" in card
        assert "card_type" in card
        assert "cost" in card
        assert "description" in card
