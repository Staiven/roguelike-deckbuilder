"""Pydantic models for API responses."""

from __future__ import annotations
from typing import Optional, List, Tuple
from pydantic import BaseModel
from enum import Enum


class CardTypeEnum(str, Enum):
    """Card types for API responses."""
    ATTACK = "ATTACK"
    SKILL = "SKILL"
    POWER = "POWER"
    STATUS = "STATUS"
    CURSE = "CURSE"


class TargetTypeEnum(str, Enum):
    """Target types for API responses."""
    SINGLE_ENEMY = "SINGLE_ENEMY"
    ALL_ENEMIES = "ALL_ENEMIES"
    SELF = "SELF"
    RANDOM_ENEMY = "RANDOM_ENEMY"
    NONE = "NONE"


class CardRarityEnum(str, Enum):
    """Card rarity for API responses."""
    STARTER = "STARTER"
    COMMON = "COMMON"
    UNCOMMON = "UNCOMMON"
    RARE = "RARE"


class IntentTypeEnum(str, Enum):
    """Enemy intent types for API responses."""
    ATTACK = "ATTACK"
    DEFEND = "DEFEND"
    BUFF = "BUFF"
    DEBUFF = "DEBUFF"
    ATTACK_DEFEND = "ATTACK_DEFEND"
    ATTACK_BUFF = "ATTACK_BUFF"
    ATTACK_DEBUFF = "ATTACK_DEBUFF"
    UNKNOWN = "UNKNOWN"
    SLEEPING = "SLEEPING"


class MapNodeTypeEnum(str, Enum):
    """Map node types for API responses."""
    COMBAT = "COMBAT"
    ELITE = "ELITE"
    REST = "REST"
    SHOP = "SHOP"
    EVENT = "EVENT"
    BOSS = "BOSS"
    TREASURE = "TREASURE"


class GameStateEnum(str, Enum):
    """Game states for API responses."""
    MAIN_MENU = "MAIN_MENU"
    MAP = "MAP"
    COMBAT = "COMBAT"
    EVENT = "EVENT"
    SHOP = "SHOP"
    REST = "REST"
    REWARD = "REWARD"
    GAME_OVER = "GAME_OVER"
    VICTORY = "VICTORY"


class CombatPhaseEnum(str, Enum):
    """Combat phases for API responses."""
    NOT_STARTED = "NOT_STARTED"
    PLAYER_TURN = "PLAYER_TURN"
    ENEMY_TURN = "ENEMY_TURN"
    COMBAT_END = "COMBAT_END"


class CombatResultEnum(str, Enum):
    """Combat results for API responses."""
    IN_PROGRESS = "IN_PROGRESS"
    VICTORY = "VICTORY"
    DEFEAT = "DEFEAT"


class StatusEffectResponse(BaseModel):
    """A single status effect."""
    type: str
    stacks: int


class CardResponse(BaseModel):
    """Response model for a card."""
    id: str
    name: str
    card_type: CardTypeEnum
    rarity: CardRarityEnum
    target_type: TargetTypeEnum
    cost: int
    description: str
    upgraded: bool
    exhaust: bool
    ethereal: bool
    innate: bool
    retain: bool
    unplayable: bool


class IntentResponse(BaseModel):
    """Response model for an enemy's intent."""
    intent_type: IntentTypeEnum
    damage: Optional[int] = None
    times: int = 1
    block: Optional[int] = None
    buff_amount: Optional[int] = None
    debuff_amount: Optional[int] = None
    display_string: str


class EnemyResponse(BaseModel):
    """Response model for an enemy."""
    id: str
    name: str
    max_hp: int
    current_hp: int
    block: int
    status_effects: List[StatusEffectResponse]
    intent: IntentResponse


class RelicResponse(BaseModel):
    """Response model for a relic."""
    id: str
    name: str
    description: str
    counter: Optional[int] = None


class PlayerResponse(BaseModel):
    """Response model for the player."""
    name: str
    max_hp: int
    current_hp: int
    gold: int
    max_energy: int
    energy: int
    block: int
    status_effects: List[StatusEffectResponse]
    deck_size: int
    relics: List[RelicResponse]


class CombatStateResponse(BaseModel):
    """Response model for combat state."""
    active: bool
    turn_number: int
    phase: CombatPhaseEnum
    result: CombatResultEnum
    player: PlayerResponse
    enemies: List[EnemyResponse]
    hand: List[CardResponse]
    draw_pile_count: int
    discard_pile_count: int
    exhaust_pile_count: int
    current_energy: int
    max_energy: int


class MapNodeResponse(BaseModel):
    """Response model for a map node."""
    row: int
    col: int
    x: float
    y: float
    node_type: MapNodeTypeEnum
    visited: bool
    available: bool
    connections: List[Tuple[int, int]]  # List of (row, col) tuples


class MapResponse(BaseModel):
    """Response model for the game map."""
    nodes: List[List[MapNodeResponse]]
    current_row: int
    current_node: Optional[Tuple[int, int]] = None  # (row, col) or None
    boss_node: Optional[MapNodeResponse] = None


class GameStateResponse(BaseModel):
    """Full game state response."""
    session_id: str
    state: GameStateEnum
    act: int
    floor: int
    ascension: int
    player: PlayerResponse
    map: Optional[MapResponse] = None
    combat: Optional[CombatStateResponse] = None
    deck: List[CardResponse]


# Request models

class NewGameRequest(BaseModel):
    """Request to create a new game."""
    character_class: str  # "warrior" or "mage"
    seed: Optional[int] = None


class MoveRequest(BaseModel):
    """Request to move to a map node."""
    row: int
    col: int


class PlayCardRequest(BaseModel):
    """Request to play a card."""
    card_index: int
    target_index: Optional[int] = None


class UpgradeCardRequest(BaseModel):
    """Request to upgrade a card at rest site."""
    card_index: int


# Response models for actions

class ActionResponse(BaseModel):
    """Generic action response."""
    success: bool
    message: Optional[str] = None
    game_state: Optional[GameStateResponse] = None


class NewGameResponse(BaseModel):
    """Response for creating a new game."""
    session_id: str
    game_state: GameStateResponse
