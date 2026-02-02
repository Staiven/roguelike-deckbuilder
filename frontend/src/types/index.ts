// Card types
export type CardType = 'attack' | 'skill' | 'power' | 'status' | 'curse';
export type TargetType = 'single_enemy' | 'all_enemies' | 'self' | 'random_enemy' | 'none';
export type CardRarity = 'starter' | 'common' | 'uncommon' | 'rare';

export interface Card {
  id: string;
  name: string;
  cost: number;
  cardType: CardType;
  targetType: TargetType;
  rarity: CardRarity;
  description: string;
  upgraded: boolean;
  exhaust: boolean;
  ethereal: boolean;
}

// Enemy types
export type IntentType = 'attack' | 'defend' | 'buff' | 'debuff' | 'attack_defend' | 'attack_buff' | 'attack_debuff' | 'unknown' | 'sleeping';

export interface Intent {
  intentType: IntentType;
  damage: number | null;
  times: number;
  block: number | null;
}

export interface Enemy {
  id: string;
  name: string;
  maxHp: number;
  currentHp: number;
  block: number;
  intent: Intent;
  statusEffects: Record<string, number>;
}

// Player types
export interface Player {
  name: string;
  maxHp: number;
  currentHp: number;
  gold: number;
  block: number;
  energy: number;
  maxEnergy: number;
  statusEffects: Record<string, number>;
}

// Combat types
export type CombatPhase = 'not_started' | 'player_turn' | 'enemy_turn' | 'combat_end';
export type CombatResult = 'in_progress' | 'victory' | 'defeat';

export interface CombatState {
  active: boolean;
  turn: number;
  phase: CombatPhase;
  result: CombatResult;
  hand: Card[];
  drawPileCount: number;
  discardPileCount: number;
  exhaustPileCount: number;
  enemies: Enemy[];
  player: Player;
}

// Map types
export type MapNodeType = 'combat' | 'elite' | 'rest' | 'shop' | 'event' | 'boss' | 'treasure';

export interface MapNode {
  row: number;
  col: number;
  nodeType: MapNodeType;
  visited: boolean;
  available: boolean;
  connections: Array<{ row: number; col: number }>;
}

export interface GameMap {
  nodes: MapNode[][];
  currentRow: number;
  currentCol: number | null;
  bossNode: MapNode | null;
}

// Game state types
export type GameState = 'main_menu' | 'map' | 'combat' | 'event' | 'shop' | 'rest' | 'reward' | 'game_over' | 'victory';

export interface FullGameState {
  sessionId: string;
  characterClass: string;
  characterName: string;
  state: GameState;
  player: Player;
  map: GameMap;
  combat: CombatState | null;
  act: number;
  floor: number;
}
