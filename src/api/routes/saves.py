"""Save/load game routes."""

from __future__ import annotations
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from src.api.database import (
    get_save_by_user_id,
    save_game,
    delete_save,
    get_user_by_username,
)
from src.api.serialization import (
    serialize_session,
    deserialize_session,
    get_save_metadata,
)


router = APIRouter(prefix="/api/save", tags=["saves"])

# Reference to the sessions dict from main - will be set by main.py
sessions: Dict[str, Any] = {}


def set_sessions_ref(sessions_dict: Dict[str, Any]) -> None:
    """Set reference to the sessions dict from main.py."""
    global sessions
    sessions = sessions_dict


class SaveRequest(BaseModel):
    """Save game request body."""
    session_id: str


class SaveResponse(BaseModel):
    """Save game response."""
    success: bool
    message: str


class LoadResponse(BaseModel):
    """Load game response."""
    success: bool
    session_id: Optional[str] = None
    game_state: Optional[dict] = None
    message: Optional[str] = None


class SaveInfoResponse(BaseModel):
    """Save info response."""
    has_save: bool
    character_class: Optional[str] = None
    character_name: Optional[str] = None
    act: Optional[int] = None
    floor: Optional[int] = None
    current_hp: Optional[int] = None
    max_hp: Optional[int] = None
    gold: Optional[int] = None
    deck_size: Optional[int] = None
    relic_count: Optional[int] = None
    updated_at: Optional[str] = None


def get_user_id_from_header(x_user_id: Optional[str]) -> int:
    """Extract and validate user ID from header."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header required")

    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")


@router.post("", response_model=SaveResponse)
def save_current_game(
    request: SaveRequest,
    x_user_id: Optional[str] = Header(None),
) -> SaveResponse:
    """
    Save the current game session.

    Requires X-User-Id header with the user's ID.
    Overwrites any existing save for this user.
    """
    user_id = get_user_id_from_header(x_user_id)

    # Get the session
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[request.session_id]

    # Serialize the session
    session_data = serialize_session(session)

    # Get metadata for the save record
    metadata = get_save_metadata(session)

    # Save to database
    save_game(
        user_id=user_id,
        session_data=session_data,
        character_class=metadata["character_class"],
        act=metadata["act"],
        floor=metadata["floor"],
        current_hp=metadata["current_hp"],
        max_hp=metadata["max_hp"],
    )

    return SaveResponse(success=True, message="Game saved successfully")


@router.post("/load", response_model=LoadResponse)
def load_saved_game(
    x_user_id: Optional[str] = Header(None),
) -> LoadResponse:
    """
    Load a saved game.

    Requires X-User-Id header with the user's ID.
    Creates a new session with the saved state.
    """
    from src.api.main import session_to_game_state

    user_id = get_user_id_from_header(x_user_id)

    # Get the save
    save = get_save_by_user_id(user_id)
    if not save:
        return LoadResponse(
            success=False,
            message="No save found for this user",
        )

    # Deserialize the session
    try:
        session = deserialize_session(save["session_data"])
    except Exception as e:
        return LoadResponse(
            success=False,
            message=f"Failed to load save: {str(e)}",
        )

    # Create a new session ID and store
    session_id = str(uuid.uuid4())
    sessions[session_id] = session

    # Get the game state response
    game_state = session_to_game_state(session_id, session)

    return LoadResponse(
        success=True,
        session_id=session_id,
        game_state=game_state.model_dump(),
    )


@router.get("/info", response_model=SaveInfoResponse)
def get_save_info(
    x_user_id: Optional[str] = Header(None),
) -> SaveInfoResponse:
    """
    Get information about a user's save without loading it.

    Requires X-User-Id header with the user's ID.
    """
    user_id = get_user_id_from_header(x_user_id)

    save = get_save_by_user_id(user_id)
    if not save:
        return SaveInfoResponse(has_save=False)

    return SaveInfoResponse(
        has_save=True,
        character_class=save["character_class"],
        act=save["act"],
        floor=save["floor"],
        current_hp=save["current_hp"],
        max_hp=save["max_hp"],
        updated_at=save["updated_at"],
    )


@router.delete("", response_model=SaveResponse)
def delete_saved_game(
    x_user_id: Optional[str] = Header(None),
) -> SaveResponse:
    """
    Delete a user's saved game.

    Requires X-User-Id header with the user's ID.
    """
    user_id = get_user_id_from_header(x_user_id)

    deleted = delete_save(user_id)

    if deleted:
        return SaveResponse(success=True, message="Save deleted successfully")
    else:
        return SaveResponse(success=False, message="No save found to delete")
