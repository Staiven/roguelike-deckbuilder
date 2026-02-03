"""Tests for save/load functionality."""

import os
import pytest
from fastapi.testclient import TestClient

from src.api.main import app, sessions
from src.api.database import init_db, get_db_path, get_user_by_username, get_save_by_user_id
from src.api.routes.saves import set_sessions_ref
from src.api.serialization import serialize_session, deserialize_session, get_save_metadata
from src.main import create_warrior_run, create_mage_run, GameState
from src.core.events import reset_event_bus


# Use a test database
TEST_DB_PATH = "test_game_saves.db"


@pytest.fixture(autouse=True)
def setup_test_db():
    """Set up test database before each test."""
    import src.api.database as db_module

    # Set test database path - update both env var and module variable
    os.environ["DATABASE_PATH"] = TEST_DB_PATH
    db_module.DATABASE_PATH = TEST_DB_PATH

    # Remove old test database
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # Initialize fresh database
    init_db()

    # Clear sessions and set the reference for saves module
    sessions.clear()
    set_sessions_ref(sessions)
    reset_event_bus()

    yield

    # Cleanup
    sessions.clear()
    reset_event_bus()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestSerialization:
    """Test serialization/deserialization of game sessions."""

    def test_serialize_warrior_session(self):
        """Test serializing a warrior session."""
        session = create_warrior_run(seed=42)
        session.start_run()

        json_str = serialize_session(session)

        assert json_str is not None
        assert "WARRIOR" in json_str
        assert "Ironclad" in json_str

    def test_serialize_mage_session(self):
        """Test serializing a mage session."""
        session = create_mage_run(seed=42)
        session.start_run()

        json_str = serialize_session(session)

        assert json_str is not None
        assert "MAGE" in json_str
        assert "Silent" in json_str

    def test_deserialize_session_roundtrip(self):
        """Test that serialize/deserialize preserves state."""
        original = create_warrior_run(seed=42)
        original.start_run()

        # Modify some state
        original.character.player.gold = 500
        original.character.player.current_hp = 50

        # Serialize and deserialize
        json_str = serialize_session(original)
        restored = deserialize_session(json_str)

        # Check state is preserved
        assert restored.character.character_class == original.character.character_class
        assert restored.character.player.gold == 500
        assert restored.character.player.current_hp == 50
        assert restored.act == original.act
        assert restored.floor == original.floor

    def test_deserialize_preserves_deck(self):
        """Test that deck is preserved through serialization."""
        original = create_warrior_run(seed=42)
        original.start_run()

        original_deck_size = len(original.character.player.master_deck)

        json_str = serialize_session(original)
        restored = deserialize_session(json_str)

        assert len(restored.character.player.master_deck) == original_deck_size

    def test_deserialize_preserves_relics(self):
        """Test that relics are preserved through serialization."""
        original = create_warrior_run(seed=42)
        original.start_run()

        original_relic_count = len(original.character.player.relics)

        json_str = serialize_session(original)
        restored = deserialize_session(json_str)

        assert len(restored.character.player.relics) == original_relic_count

    def test_get_save_metadata(self):
        """Test getting save metadata."""
        session = create_warrior_run(seed=42)
        session.start_run()

        metadata = get_save_metadata(session)

        assert metadata["character_class"] == "WARRIOR"
        assert metadata["character_name"] == "Ironclad"
        assert metadata["current_hp"] == 80
        assert metadata["max_hp"] == 80


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_login_creates_user(self, client):
        """Test that login creates a new user."""
        import uuid
        unique_username = f"newuser_{uuid.uuid4().hex[:8]}"

        response = client.post(
            "/api/auth/login",
            json={"username": unique_username}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["username"] == unique_username
        assert data["user_id"] > 0
        assert data["has_save"] is False

    def test_login_returns_existing_user(self, client):
        """Test that login returns existing user."""
        # First login
        response1 = client.post(
            "/api/auth/login",
            json={"username": "testuser"}
        )
        user_id = response1.json()["user_id"]

        # Second login
        response2 = client.post(
            "/api/auth/login",
            json={"username": "testuser"}
        )

        assert response2.json()["user_id"] == user_id

    def test_login_empty_username(self, client):
        """Test that empty username is rejected."""
        response = client.post(
            "/api/auth/login",
            json={"username": ""}
        )

        assert response.status_code == 400


class TestSaveEndpoints:
    """Test save/load endpoints."""

    def _create_game_and_login(self, client) -> tuple[str, int]:
        """Helper to create a game and login."""
        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser"}
        )
        user_id = login_response.json()["user_id"]

        # Create game
        game_response = client.post(
            "/api/game/new",
            json={"character_class": "warrior", "seed": 42}
        )
        session_id = game_response.json()["session_id"]

        return session_id, user_id

    def test_save_game(self, client):
        """Test saving a game."""
        session_id, user_id = self._create_game_and_login(client)

        response = client.post(
            "/api/save",
            json={"session_id": session_id},
            headers={"X-User-Id": str(user_id)}
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_save_requires_user_id(self, client):
        """Test that save requires X-User-Id header."""
        session_id, _ = self._create_game_and_login(client)

        response = client.post(
            "/api/save",
            json={"session_id": session_id}
        )

        assert response.status_code == 401

    def test_load_game(self, client):
        """Test loading a saved game."""
        session_id, user_id = self._create_game_and_login(client)

        # Save the game
        client.post(
            "/api/save",
            json={"session_id": session_id},
            headers={"X-User-Id": str(user_id)}
        )

        # Load the game
        response = client.post(
            "/api/save/load",
            headers={"X-User-Id": str(user_id)}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] is not None
        assert data["game_state"] is not None

    def test_load_no_save(self, client):
        """Test loading when no save exists."""
        # Login but don't save
        login_response = client.post(
            "/api/auth/login",
            json={"username": "newuser"}
        )
        user_id = login_response.json()["user_id"]

        response = client.post(
            "/api/save/load",
            headers={"X-User-Id": str(user_id)}
        )

        assert response.status_code == 200
        assert response.json()["success"] is False

    def test_save_info(self, client):
        """Test getting save info."""
        session_id, user_id = self._create_game_and_login(client)

        # Save the game
        client.post(
            "/api/save",
            json={"session_id": session_id},
            headers={"X-User-Id": str(user_id)}
        )

        # Get save info
        response = client.get(
            "/api/save/info",
            headers={"X-User-Id": str(user_id)}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_save"] is True
        assert data["character_class"] == "WARRIOR"

    def test_delete_save(self, client):
        """Test deleting a save."""
        session_id, user_id = self._create_game_and_login(client)

        # Save the game
        client.post(
            "/api/save",
            json={"session_id": session_id},
            headers={"X-User-Id": str(user_id)}
        )

        # Delete the save
        response = client.delete(
            "/api/save",
            headers={"X-User-Id": str(user_id)}
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify save is gone
        info_response = client.get(
            "/api/save/info",
            headers={"X-User-Id": str(user_id)}
        )
        assert info_response.json()["has_save"] is False

    def test_save_overwrites_existing(self, client):
        """Test that saving overwrites existing save."""
        session_id, user_id = self._create_game_and_login(client)

        # Save first time
        client.post(
            "/api/save",
            json={"session_id": session_id},
            headers={"X-User-Id": str(user_id)}
        )

        # Modify the session
        sessions[session_id].character.player.gold = 999

        # Save again
        response = client.post(
            "/api/save",
            json={"session_id": session_id},
            headers={"X-User-Id": str(user_id)}
        )

        assert response.json()["success"] is True

        # Load and verify gold is updated
        load_response = client.post(
            "/api/save/load",
            headers={"X-User-Id": str(user_id)}
        )

        game_state = load_response.json()["game_state"]
        assert game_state["player"]["gold"] == 999
