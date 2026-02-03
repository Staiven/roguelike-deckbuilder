"""Authentication routes - simple username-based login."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.api.database import get_or_create_user, has_save


router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Login request body."""
    username: str


class LoginResponse(BaseModel):
    """Login response."""
    success: bool
    user_id: int
    username: str
    has_save: bool


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    """
    Login or register with a username.

    If the username doesn't exist, a new user is created.
    Returns whether the user has an existing save.
    """
    username = request.username.strip()

    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    if len(username) > 50:
        raise HTTPException(status_code=400, detail="Username too long (max 50 characters)")

    user = get_or_create_user(username)
    user_has_save = has_save(user["id"])

    return LoginResponse(
        success=True,
        user_id=user["id"],
        username=user["username"],
        has_save=user_has_save,
    )
