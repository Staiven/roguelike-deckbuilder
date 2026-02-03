"""FastAPI application for the roguelike deck-builder game."""

from __future__ import annotations
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.database import init_db
from src.api.routes.auth import router as auth_router
from src.api.routes.saves import router as saves_router, set_sessions_ref
from src.api.schemas import (
    # Enums
    CardTypeEnum,
    TargetTypeEnum,
    CardRarityEnum,
    IntentTypeEnum,
    MapNodeTypeEnum,
    GameStateEnum,
    CombatPhaseEnum,
    CombatResultEnum,
    # Response models
    CardResponse,
    EnemyResponse,
    PlayerResponse,
    RelicResponse,
    StatusEffectResponse,
    IntentResponse,
    CombatStateResponse,
    MapNodeResponse,
    MapResponse,
    GameStateResponse,
    # Request models
    NewGameRequest,
    MoveRequest,
    PlayCardRequest,
    UpgradeCardRequest,
    # Action responses
    ActionResponse,
    NewGameResponse,
)
from src.main import GameSession, GameState, create_warrior_run, create_mage_run
from src.combat.combat_manager import CombatResult, CombatPhase


# In-memory session storage
sessions: Dict[str, GameSession] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    set_sessions_ref(sessions)
    yield


app = FastAPI(
    title="Roguelike Deck-Builder API",
    description="Backend API for the roguelike deck-builder game",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware - allow all origins for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register auth and save routes
app.include_router(auth_router)
app.include_router(saves_router)


# Helper functions to convert game objects to response models

def card_to_response(card: Any) -> CardResponse:
    """Convert a CardInstance to CardResponse."""
    return CardResponse(
        id=card.id,
        name=card.name,
        card_type=CardTypeEnum(card.card_type.name),
        rarity=CardRarityEnum(card.rarity.name),
        target_type=TargetTypeEnum(card.target_type.name),
        cost=card.cost,
        description=card.description,
        upgraded=card.upgraded,
        exhaust=card.exhaust,
        ethereal=card.ethereal,
        innate=card.innate,
        retain=card.retain,
        unplayable=card.unplayable,
    )


def enemy_to_response(enemy: Any) -> EnemyResponse:
    """Convert an Enemy to EnemyResponse."""
    status_effects = [
        StatusEffectResponse(type=effect_type.name, stacks=stacks)
        for effect_type, stacks in enemy.status_effects.items()
    ]

    intent_response = IntentResponse(
        intent_type=IntentTypeEnum(enemy.intent.intent_type.name),
        damage=enemy.intent.damage,
        times=enemy.intent.times,
        block=enemy.intent.block,
        buff_amount=enemy.intent.buff_amount,
        debuff_amount=enemy.intent.debuff_amount,
        display_string=enemy.intent.get_display_string(),
    )

    return EnemyResponse(
        id=enemy.id,
        name=enemy.name,
        max_hp=enemy.max_hp,
        current_hp=enemy.current_hp,
        block=enemy.block,
        status_effects=status_effects,
        intent=intent_response,
    )


def player_to_response(player: Any) -> PlayerResponse:
    """Convert a Player to PlayerResponse."""
    status_effects = [
        StatusEffectResponse(type=effect_type.name, stacks=stacks)
        for effect_type, stacks in player.status_effects.items()
    ]

    relics = [
        RelicResponse(
            id=relic.data.id,
            name=relic.data.name,
            description=relic.data.description,
            counter=getattr(relic, 'counter', None),
        )
        for relic in player.relics
    ]

    return PlayerResponse(
        name=player.name,
        max_hp=player.max_hp,
        current_hp=player.current_hp,
        gold=player.gold,
        max_energy=player.max_energy,
        energy=player.energy,
        block=player.block,
        status_effects=status_effects,
        deck_size=len(player.master_deck),
        relics=relics,
    )


def combat_to_response(session: GameSession) -> Optional[CombatStateResponse]:
    """Convert combat state to CombatStateResponse."""
    if session.state != GameState.COMBAT:
        return None

    combat = session.combat_manager
    state = combat.state

    if state is None:
        return None

    return CombatStateResponse(
        active=True,
        turn_number=state.turn_number,
        phase=CombatPhaseEnum(state.phase.name),
        result=CombatResultEnum(state.result.name),
        player=player_to_response(state.player),
        enemies=[enemy_to_response(e) for e in state.get_living_enemies()],
        hand=[card_to_response(c) for c in state.hand],
        draw_pile_count=len(state.draw_pile),
        discard_pile_count=len(state.discard_pile),
        exhaust_pile_count=len(state.exhaust_pile),
        current_energy=state.current_energy,
        max_energy=state.energy_system.max_energy,
    )


def map_node_to_response(node: Any) -> MapNodeResponse:
    """Convert a MapNode to MapNodeResponse."""
    connections = [(conn.row, conn.col) for conn in node.connections]

    return MapNodeResponse(
        row=node.row,
        col=node.col,
        x=node.x,
        y=node.y,
        node_type=MapNodeTypeEnum(node.node_type.name),
        visited=node.visited,
        available=node.available,
        connections=connections,
    )


def map_to_response(session: GameSession) -> Optional[MapResponse]:
    """Convert game map to MapResponse."""
    game_map = session.current_map

    if game_map is None:
        return None

    nodes = [
        [map_node_to_response(node) for node in row]
        for row in game_map.nodes
    ]

    current_node = None
    if game_map.current_node:
        current_node = (game_map.current_node.row, game_map.current_node.col)

    boss_node = None
    if game_map.boss_node:
        boss_node = map_node_to_response(game_map.boss_node)

    return MapResponse(
        nodes=nodes,
        current_row=game_map.current_row,
        current_node=current_node,
        boss_node=boss_node,
    )


def session_to_game_state(session_id: str, session: GameSession) -> GameStateResponse:
    """Convert a GameSession to GameStateResponse."""
    player = session.character.player

    return GameStateResponse(
        session_id=session_id,
        state=GameStateEnum(session.state.name),
        act=session.act,
        floor=session.floor,
        ascension=session.ascension,
        player=player_to_response(player),
        map=map_to_response(session),
        combat=combat_to_response(session),
        deck=[card_to_response(c) for c in player.master_deck],
    )


def get_session(session_id: str) -> GameSession:
    """Get a session by ID or raise 404."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return sessions[session_id]


# API Endpoints

@app.post("/api/game/new", response_model=NewGameResponse)
def create_new_game(request: NewGameRequest) -> NewGameResponse:
    """Create a new game session."""
    session_id = str(uuid.uuid4())

    character_class = request.character_class.lower()
    if character_class == "warrior":
        session = create_warrior_run(seed=request.seed)
    elif character_class == "mage":
        session = create_mage_run(seed=request.seed)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid character class: {request.character_class}. Must be 'warrior' or 'mage'."
        )

    session.start_run()
    sessions[session_id] = session

    return NewGameResponse(
        session_id=session_id,
        game_state=session_to_game_state(session_id, session),
    )


@app.get("/api/game/{session_id}/state", response_model=GameStateResponse)
def get_game_state(session_id: str) -> GameStateResponse:
    """Get the full game state for a session."""
    session = get_session(session_id)
    return session_to_game_state(session_id, session)


@app.post("/api/game/{session_id}/move", response_model=ActionResponse)
def move_to_node(session_id: str, request: MoveRequest) -> ActionResponse:
    """Move to a map node."""
    session = get_session(session_id)

    if session.state != GameState.MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot move while in state: {session.state.name}"
        )

    if session.current_map is None:
        raise HTTPException(status_code=400, detail="No map available")

    # Find the target node
    target_node = None
    for row in session.current_map.nodes:
        for node in row:
            if node.row == request.row and node.col == request.col:
                target_node = node
                break
        if target_node:
            break

    # Also check boss node
    if session.current_map.boss_node:
        boss = session.current_map.boss_node
        if boss.row == request.row and boss.col == request.col:
            target_node = boss

    if target_node is None:
        raise HTTPException(status_code=400, detail=f"Node not found at ({request.row}, {request.col})")

    success = session.move_to_node(target_node)

    if not success:
        return ActionResponse(
            success=False,
            message="Cannot move to that node",
            game_state=session_to_game_state(session_id, session),
        )

    return ActionResponse(
        success=True,
        message=f"Moved to {target_node.node_type.name} node",
        game_state=session_to_game_state(session_id, session),
    )


@app.post("/api/game/{session_id}/combat/play-card", response_model=ActionResponse)
def play_card(session_id: str, request: PlayCardRequest) -> ActionResponse:
    """Play a card from hand."""
    session = get_session(session_id)

    if session.state != GameState.COMBAT:
        raise HTTPException(status_code=400, detail="Not in combat")

    combat = session.combat_manager
    state = combat.state

    if state is None:
        raise HTTPException(status_code=400, detail="Combat not initialized")

    if request.card_index < 0 or request.card_index >= len(state.hand):
        raise HTTPException(status_code=400, detail=f"Invalid card index: {request.card_index}")

    card = state.hand[request.card_index]

    # Determine target
    target = None
    if request.target_index is not None:
        living_enemies = state.get_living_enemies()
        if request.target_index < 0 or request.target_index >= len(living_enemies):
            raise HTTPException(status_code=400, detail=f"Invalid target index: {request.target_index}")
        target = living_enemies[request.target_index]

    result = combat.play_card(card, target)

    # Check if combat ended
    if state.result == CombatResult.VICTORY:
        session.end_combat(victory=True)
    elif state.result == CombatResult.DEFEAT:
        session.end_combat(victory=False)

    return ActionResponse(
        success=result["success"],
        message=result.get("reason"),
        game_state=session_to_game_state(session_id, session),
    )


@app.post("/api/game/{session_id}/combat/end-turn", response_model=ActionResponse)
def end_turn(session_id: str) -> ActionResponse:
    """End the player's turn."""
    session = get_session(session_id)

    if session.state != GameState.COMBAT:
        raise HTTPException(status_code=400, detail="Not in combat")

    combat = session.combat_manager
    state = combat.state

    if state is None:
        raise HTTPException(status_code=400, detail="Combat not initialized")

    result = combat.end_player_turn()

    # Check if combat ended
    if state.result == CombatResult.VICTORY:
        session.end_combat(victory=True)
    elif state.result == CombatResult.DEFEAT:
        session.end_combat(victory=False)

    return ActionResponse(
        success=result["success"],
        message=result.get("reason"),
        game_state=session_to_game_state(session_id, session),
    )


@app.post("/api/game/{session_id}/rest/heal", response_model=ActionResponse)
def rest_heal(session_id: str) -> ActionResponse:
    """Rest at a campfire to heal."""
    session = get_session(session_id)

    if session.state != GameState.REST:
        raise HTTPException(status_code=400, detail="Not at a rest site")

    healed = session.rest_heal()

    return ActionResponse(
        success=True,
        message=f"Healed for {healed} HP",
        game_state=session_to_game_state(session_id, session),
    )


@app.post("/api/game/{session_id}/rest/upgrade", response_model=ActionResponse)
def rest_upgrade(session_id: str, request: UpgradeCardRequest) -> ActionResponse:
    """Upgrade a card at a rest site."""
    session = get_session(session_id)

    if session.state != GameState.REST:
        raise HTTPException(status_code=400, detail="Not at a rest site")

    player = session.character.player

    if request.card_index < 0 or request.card_index >= len(player.master_deck):
        raise HTTPException(status_code=400, detail=f"Invalid card index: {request.card_index}")

    card = player.master_deck[request.card_index]

    if not card.can_upgrade():
        return ActionResponse(
            success=False,
            message="Card cannot be upgraded",
            game_state=session_to_game_state(session_id, session),
        )

    card.upgrade()
    session.rest_upgrade()

    return ActionResponse(
        success=True,
        message=f"Upgraded {card.name}",
        game_state=session_to_game_state(session_id, session),
    )


@app.post("/api/game/{session_id}/reward/skip", response_model=ActionResponse)
def skip_reward(session_id: str) -> ActionResponse:
    """Skip rewards and return to the map."""
    session = get_session(session_id)

    if session.state != GameState.REWARD:
        raise HTTPException(status_code=400, detail="Not in reward screen")

    session.collect_reward()

    return ActionResponse(
        success=True,
        message="Returned to map",
        game_state=session_to_game_state(session_id, session),
    )


@app.get("/api/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
