import type { FullGameState, Card, Enemy, Player, MapNode, GameMap, CombatState, Intent } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Transform snake_case API response to camelCase frontend types
function transformCard(apiCard: any): Card {
  return {
    id: apiCard.id,
    name: apiCard.name,
    cost: apiCard.cost,
    cardType: apiCard.card_type.toLowerCase(),
    targetType: apiCard.target_type.toLowerCase(),
    rarity: apiCard.rarity.toLowerCase(),
    description: apiCard.description,
    upgraded: apiCard.upgraded,
    exhaust: apiCard.exhaust,
    ethereal: apiCard.ethereal,
  };
}

function transformIntent(apiIntent: any): Intent {
  return {
    intentType: apiIntent.intent_type.toLowerCase(),
    damage: apiIntent.damage,
    times: apiIntent.times,
    block: apiIntent.block,
  };
}

function transformEnemy(apiEnemy: any): Enemy {
  const statusEffects: Record<string, number> = {};
  if (apiEnemy.status_effects) {
    apiEnemy.status_effects.forEach((se: any) => {
      statusEffects[se.type.toLowerCase()] = se.stacks;
    });
  }
  return {
    id: apiEnemy.id,
    name: apiEnemy.name,
    maxHp: apiEnemy.max_hp,
    currentHp: apiEnemy.current_hp,
    block: apiEnemy.block,
    intent: transformIntent(apiEnemy.intent),
    statusEffects,
  };
}

function transformPlayer(apiPlayer: any): Player {
  const statusEffects: Record<string, number> = {};
  if (apiPlayer.status_effects) {
    apiPlayer.status_effects.forEach((se: any) => {
      statusEffects[se.type.toLowerCase()] = se.stacks;
    });
  }
  return {
    name: apiPlayer.name,
    maxHp: apiPlayer.max_hp,
    currentHp: apiPlayer.current_hp,
    gold: apiPlayer.gold,
    block: apiPlayer.block,
    energy: apiPlayer.energy,
    maxEnergy: apiPlayer.max_energy,
    statusEffects,
  };
}

function transformMapNode(apiNode: any): MapNode {
  return {
    row: apiNode.row,
    col: apiNode.col,
    nodeType: apiNode.node_type.toLowerCase(),
    visited: apiNode.visited,
    available: apiNode.available,
    connections: apiNode.connections.map((c: [number, number]) => ({ row: c[0], col: c[1] })),
  };
}

function transformMap(apiMap: any): GameMap {
  return {
    nodes: apiMap.nodes.map((row: any[]) => row.map(transformMapNode)),
    currentRow: apiMap.current_row,
    currentCol: apiMap.current_col,
    bossNode: apiMap.boss_node ? transformMapNode(apiMap.boss_node) : null,
  };
}

function transformCombat(apiCombat: any): CombatState | null {
  if (!apiCombat || !apiCombat.active) {
    return null;
  }
  return {
    active: apiCombat.active,
    turn: apiCombat.turn,
    phase: apiCombat.phase.toLowerCase(),
    result: apiCombat.result.toLowerCase(),
    hand: apiCombat.hand.map(transformCard),
    drawPileCount: apiCombat.draw_pile_count,
    discardPileCount: apiCombat.discard_pile_count,
    exhaustPileCount: apiCombat.exhaust_pile_count,
    enemies: apiCombat.enemies.map(transformEnemy),
    player: transformPlayer(apiCombat.player),
  };
}

function transformGameState(apiResponse: any): FullGameState {
  // Handle both direct game_state and wrapped response
  const gameState = apiResponse.game_state || apiResponse;

  return {
    sessionId: gameState.session_id,
    characterClass: gameState.character_class || 'warrior',
    characterName: gameState.character_name || gameState.player?.name || 'Unknown',
    state: gameState.state.toLowerCase(),
    player: transformPlayer(gameState.player),
    map: transformMap(gameState.map),
    combat: gameState.combat ? transformCombat(gameState.combat) : null,
    act: gameState.act,
    floor: gameState.floor,
  };
}

export async function createGame(characterClass: 'warrior' | 'mage', seed?: number): Promise<FullGameState> {
  const response = await fetch(`${API_BASE}/game/new`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ character_class: characterClass, seed }),
  });
  if (!response.ok) {
    throw new Error(`Failed to create game: ${response.statusText}`);
  }
  const data = await response.json();
  return transformGameState(data);
}

export async function getGameState(sessionId: string): Promise<FullGameState> {
  const response = await fetch(`${API_BASE}/game/${sessionId}/state`);
  if (!response.ok) {
    throw new Error(`Failed to get game state: ${response.statusText}`);
  }
  const data = await response.json();
  return transformGameState(data);
}

export async function moveToNode(sessionId: string, row: number, col: number): Promise<FullGameState> {
  const response = await fetch(`${API_BASE}/game/${sessionId}/move`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ row, col }),
  });
  if (!response.ok) {
    throw new Error(`Failed to move: ${response.statusText}`);
  }
  const data = await response.json();
  return transformGameState(data);
}

export async function playCard(sessionId: string, cardIndex: number, targetIndex?: number): Promise<FullGameState> {
  const response = await fetch(`${API_BASE}/game/${sessionId}/combat/play-card`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ card_index: cardIndex, target_index: targetIndex }),
  });
  if (!response.ok) {
    throw new Error(`Failed to play card: ${response.statusText}`);
  }
  const data = await response.json();
  return transformGameState(data);
}

export async function endTurn(sessionId: string): Promise<FullGameState> {
  const response = await fetch(`${API_BASE}/game/${sessionId}/combat/end-turn`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to end turn: ${response.statusText}`);
  }
  const data = await response.json();
  return transformGameState(data);
}

export async function restHeal(sessionId: string): Promise<FullGameState> {
  const response = await fetch(`${API_BASE}/game/${sessionId}/rest/heal`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to heal: ${response.statusText}`);
  }
  const data = await response.json();
  return transformGameState(data);
}

export async function restUpgrade(sessionId: string, cardIndex: number): Promise<FullGameState> {
  const response = await fetch(`${API_BASE}/game/${sessionId}/rest/upgrade`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ card_index: cardIndex }),
  });
  if (!response.ok) {
    throw new Error(`Failed to upgrade: ${response.statusText}`);
  }
  const data = await response.json();
  return transformGameState(data);
}

export async function skipReward(sessionId: string): Promise<FullGameState> {
  const response = await fetch(`${API_BASE}/game/${sessionId}/reward/skip`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to skip reward: ${response.statusText}`);
  }
  const data = await response.json();
  return transformGameState(data);
}
