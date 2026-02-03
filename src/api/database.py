"""SQLite database setup for game saves."""

from __future__ import annotations
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional

# Database path - can be overridden by environment variable
DATABASE_PATH = os.environ.get("DATABASE_PATH", "game_saves.db")

# Maximum number of users allowed
MAX_USERS = int(os.environ.get("MAX_USERS", "100"))


def get_db_path() -> str:
    """Get the database file path."""
    return DATABASE_PATH


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Get a database connection as a context manager."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize the database with required tables."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Users table (simple, no passwords)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Game saves table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                session_data TEXT NOT NULL,
                character_class TEXT NOT NULL,
                act INTEGER NOT NULL,
                floor INTEGER NOT NULL,
                current_hp INTEGER NOT NULL,
                max_hp INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            )
        """)

        conn.commit()


# User operations

def get_user_count() -> int:
    """Get the total number of users."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]


def is_user_limit_reached() -> bool:
    """Check if the maximum user limit has been reached."""
    return get_user_count() >= MAX_USERS


def get_user_by_username(username: str) -> Optional[dict]:
    """Get a user by username."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def create_user(username: str) -> int:
    """Create a new user and return their ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        return cursor.lastrowid


def get_or_create_user(username: str) -> dict:
    """Get existing user or create new one."""
    user = get_user_by_username(username)
    if user:
        return user

    user_id = create_user(username)
    return {"id": user_id, "username": username}


# Save operations

def get_save_by_user_id(user_id: int) -> Optional[dict]:
    """Get a save by user ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM saves WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def save_game(
    user_id: int,
    session_data: str,
    character_class: str,
    act: int,
    floor: int,
    current_hp: int,
    max_hp: int,
) -> int:
    """Save or update a game. Returns the save ID."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Check if save exists
        existing = get_save_by_user_id(user_id)

        if existing:
            # Update existing save
            cursor.execute("""
                UPDATE saves
                SET session_data = ?,
                    character_class = ?,
                    act = ?,
                    floor = ?,
                    current_hp = ?,
                    max_hp = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (session_data, character_class, act, floor, current_hp, max_hp, user_id))
            conn.commit()
            return existing["id"]
        else:
            # Create new save
            cursor.execute("""
                INSERT INTO saves (user_id, session_data, character_class, act, floor, current_hp, max_hp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, session_data, character_class, act, floor, current_hp, max_hp))
            conn.commit()
            return cursor.lastrowid


def delete_save(user_id: int) -> bool:
    """Delete a user's save. Returns True if deleted."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saves WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0


def has_save(user_id: int) -> bool:
    """Check if a user has a save."""
    return get_save_by_user_id(user_id) is not None
