"""Serialization/deserialization for game state persistence."""

from __future__ import annotations
import json
from typing import Any

from src.main import GameSession, GameState
from src.characters.base_character import Character, CharacterClass, get_character_definition
from src.entities.card import CardInstance
from src.entities.relic import RelicInstance
from src.entities.player import Player
from src.map.map_generator import MapGenerator, GameMap, MapNode


# Card registry - combine all card registries
def get_card_data(card_id: str):
    """Get CardData by ID from all registries."""
    from src.data.cards.starter_cards import STARTER_CARD_REGISTRY
    from src.data.cards.common_cards import COMMON_CARD_REGISTRY

    if card_id in STARTER_CARD_REGISTRY:
        return STARTER_CARD_REGISTRY[card_id]
    if card_id in COMMON_CARD_REGISTRY:
        return COMMON_CARD_REGISTRY[card_id]
    return None


# Relic registry
def get_relic_data(relic_id: str):
    """Get RelicData by ID."""
    from src.data.relics.common_relics import RELIC_REGISTRY
    return RELIC_REGISTRY.get(relic_id)


def serialize_card(card: CardInstance) -> dict[str, Any]:
    """Serialize a card instance."""
    return {
        "card_id": card.data.id,
        "upgraded": card.upgraded,
    }


def deserialize_card(data: dict[str, Any]) -> CardInstance | None:
    """Deserialize a card instance."""
    card_data = get_card_data(data["card_id"])
    if card_data is None:
        return None

    card = CardInstance(data=card_data)
    if data.get("upgraded", False):
        card.upgrade()
    return card


def serialize_relic(relic: RelicInstance) -> dict[str, Any]:
    """Serialize a relic instance."""
    return {
        "relic_id": relic.data.id,
        "counter": relic.counter,
        "enabled": relic.enabled,
    }


def deserialize_relic(data: dict[str, Any]) -> RelicInstance | None:
    """Deserialize a relic instance."""
    relic_data = get_relic_data(data["relic_id"])
    if relic_data is None:
        return None

    relic = RelicInstance(data=relic_data)
    relic.counter = data.get("counter", 0)
    relic.enabled = data.get("enabled", True)
    return relic


def serialize_player(player: Player) -> dict[str, Any]:
    """Serialize player state."""
    return {
        "name": player.name,
        "max_hp": player.max_hp,
        "current_hp": player.current_hp,
        "gold": player.gold,
        "max_energy": player.max_energy,
        "deck": [serialize_card(card) for card in player.master_deck],
        "relics": [serialize_relic(relic) for relic in player.relics],
        "status_effects": {k.name: v for k, v in player.status_effects.items()},
    }


def deserialize_player(data: dict[str, Any], player: Player) -> None:
    """Deserialize player state into existing player object."""
    player.name = data["name"]
    player.max_hp = data["max_hp"]
    player.current_hp = data["current_hp"]
    player.gold = data["gold"]
    player.max_energy = data.get("max_energy", 3)

    # Rebuild deck
    player.master_deck = []
    for card_data in data.get("deck", []):
        card = deserialize_card(card_data)
        if card:
            player.master_deck.append(card)

    # Rebuild relics
    player.relics = []
    for relic_data in data.get("relics", []):
        relic = deserialize_relic(relic_data)
        if relic:
            player.relics.append(relic)

    # Rebuild status effects
    from src.core.enums import StatusEffectType
    player.status_effects = {}
    for effect_name, stacks in data.get("status_effects", {}).items():
        try:
            effect_type = StatusEffectType[effect_name]
            player.status_effects[effect_type] = stacks
        except KeyError:
            pass  # Unknown status effect, skip


def serialize_map(game_map: GameMap, seed: int | None) -> dict[str, Any]:
    """Serialize map state."""
    visited = []
    for row in game_map.nodes:
        for node in row:
            if node.visited:
                visited.append([node.row, node.col])

    current_pos = None
    if game_map.current_node:
        current_pos = [game_map.current_node.row, game_map.current_node.col]

    return {
        "seed": seed,
        "current_row": game_map.current_row,
        "current_pos": current_pos,
        "visited": visited,
    }


def deserialize_map(data: dict[str, Any]) -> GameMap:
    """Deserialize map from seed and visited state."""
    seed = data.get("seed")
    generator = MapGenerator()
    game_map = generator.generate(seed=seed)

    # Mark visited nodes
    visited_set = set(tuple(v) for v in data.get("visited", []))
    for row in game_map.nodes:
        for node in row:
            if (node.row, node.col) in visited_set:
                node.visited = True

    # Set current position
    game_map.current_row = data.get("current_row", -1)
    current_pos = data.get("current_pos")

    # Clear all available flags first
    for row in game_map.nodes:
        for node in row:
            node.available = False

    if current_pos:
        row, col = current_pos
        for node_row in game_map.nodes:
            for node in node_row:
                if node.row == row and node.col == col:
                    game_map.current_node = node
                    # Mark connected nodes as available
                    for connected in node.connections:
                        connected.available = True
                    break
    else:
        # At start, first row is available
        if game_map.nodes:
            for node in game_map.nodes[0]:
                node.available = True

    return game_map


def serialize_session(session: GameSession) -> str:
    """Serialize a complete game session to JSON string."""
    data = {
        "version": 1,
        "character_class": session.character.character_class.name,
        "state": session.state.name,
        "act": session.act,
        "floor": session.floor,
        "ascension": session.ascension,
        "seed": session.seed,
        "player": serialize_player(session.character.player),
    }

    # Serialize map if it exists
    if session.current_map:
        data["map"] = serialize_map(session.current_map, session.seed)

    # Note: We don't save mid-combat state for simplicity
    # If player is mid-combat, they'll need to restart the combat

    return json.dumps(data)


def deserialize_session(json_str: str) -> GameSession:
    """Deserialize a game session from JSON string."""
    data = json.loads(json_str)

    # Get character class
    char_class = CharacterClass[data["character_class"]]

    # Create character
    character = Character.create(char_class)

    # Restore player state
    deserialize_player(data["player"], character.player)

    # Create session
    session = GameSession(
        character=character,
        act=data.get("act", 1),
        floor=data.get("floor", 0),
        ascension=data.get("ascension", 0),
        seed=data.get("seed"),
    )

    # Restore game state
    state_name = data.get("state", "MAP")
    try:
        session.state = GameState[state_name]
    except KeyError:
        session.state = GameState.MAP

    # Restore map
    if "map" in data:
        session.current_map = deserialize_map(data["map"])

    # If they were in combat, put them back on map
    if session.state == GameState.COMBAT:
        session.state = GameState.MAP

    return session


def get_save_metadata(session: GameSession) -> dict[str, Any]:
    """Get metadata for a save without full serialization."""
    return {
        "character_class": session.character.character_class.name,
        "character_name": session.character.name,
        "act": session.act,
        "floor": session.floor,
        "current_hp": session.character.player.current_hp,
        "max_hp": session.character.player.max_hp,
        "gold": session.character.player.gold,
        "deck_size": len(session.character.player.master_deck),
        "relic_count": len(session.character.player.relics),
    }
