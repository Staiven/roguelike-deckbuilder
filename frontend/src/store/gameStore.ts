import { create } from 'zustand';
import type { FullGameState } from '../types';
import * as api from '../api/client';

interface GameStore {
  gameState: FullGameState | null;
  loading: boolean;
  error: string | null;
  selectedCard: number | null;

  // Actions
  startNewGame: (characterClass: 'warrior' | 'mage') => Promise<void>;
  refreshState: () => Promise<void>;
  moveToNode: (row: number, col: number) => Promise<void>;
  selectCard: (index: number | null) => void;
  playCard: (cardIndex: number, targetIndex?: number) => Promise<void>;
  endTurn: () => Promise<void>;
  restHeal: () => Promise<void>;
  restUpgrade: (cardIndex: number) => Promise<void>;
  skipReward: () => Promise<void>;
  setError: (error: string | null) => void;
}

export const useGameStore = create<GameStore>((set, get) => ({
  gameState: null,
  loading: false,
  error: null,
  selectedCard: null,

  startNewGame: async (characterClass) => {
    set({ loading: true, error: null });
    try {
      const state = await api.createGame(characterClass);
      set({ gameState: state, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  refreshState: async () => {
    const { gameState } = get();
    if (!gameState) return;
    try {
      const state = await api.getGameState(gameState.sessionId);
      set({ gameState: state });
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  moveToNode: async (row, col) => {
    const { gameState } = get();
    if (!gameState) return;
    set({ loading: true });
    try {
      const state = await api.moveToNode(gameState.sessionId, row, col);
      set({ gameState: state, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  selectCard: (index) => set({ selectedCard: index }),

  playCard: async (cardIndex, targetIndex) => {
    const { gameState } = get();
    if (!gameState) return;
    set({ loading: true, selectedCard: null });
    try {
      const state = await api.playCard(gameState.sessionId, cardIndex, targetIndex);
      set({ gameState: state, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  endTurn: async () => {
    const { gameState } = get();
    if (!gameState) return;
    set({ loading: true });
    try {
      const state = await api.endTurn(gameState.sessionId);
      set({ gameState: state, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  restHeal: async () => {
    const { gameState } = get();
    if (!gameState) return;
    set({ loading: true });
    try {
      const state = await api.restHeal(gameState.sessionId);
      set({ gameState: state, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  restUpgrade: async (cardIndex) => {
    const { gameState } = get();
    if (!gameState) return;
    set({ loading: true });
    try {
      const state = await api.restUpgrade(gameState.sessionId, cardIndex);
      set({ gameState: state, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  skipReward: async () => {
    const { gameState } = get();
    if (!gameState) return;
    set({ loading: true });
    try {
      const state = await api.skipReward(gameState.sessionId);
      set({ gameState: state, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  setError: (error) => set({ error }),
}));
