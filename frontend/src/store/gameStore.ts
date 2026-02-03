import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { FullGameState } from '../types';
import * as api from '../api/client';

interface UserState {
  userId: number | null;
  username: string | null;
  hasSave: boolean;
}

interface GameStore {
  // User state
  user: UserState;

  // Game state
  gameState: FullGameState | null;
  loading: boolean;
  error: string | null;
  selectedCard: number | null;

  // Auth actions
  login: (username: string) => Promise<void>;
  logout: () => void;

  // Save actions
  saveGame: () => Promise<void>;
  loadGame: () => Promise<void>;
  deleteSave: () => Promise<void>;
  refreshSaveInfo: () => Promise<void>;

  // Game actions
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

export const useGameStore = create<GameStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: { userId: null, username: null, hasSave: false },
      gameState: null,
      loading: false,
      error: null,
      selectedCard: null,

      // Auth actions
      login: async (username) => {
        set({ loading: true, error: null });
        try {
          const response = await api.login(username);
          set({
            user: {
              userId: response.user_id,
              username: response.username,
              hasSave: response.has_save,
            },
            loading: false,
          });
        } catch (e) {
          set({ error: (e as Error).message, loading: false });
        }
      },

      logout: () => {
        set({
          user: { userId: null, username: null, hasSave: false },
          gameState: null,
        });
      },

      // Save actions
      saveGame: async () => {
        const { gameState, user } = get();
        if (!gameState || !user.userId) return;
        set({ loading: true, error: null });
        try {
          await api.saveGame(gameState.sessionId, user.userId);
          set({ user: { ...user, hasSave: true }, loading: false });
        } catch (e) {
          set({ error: (e as Error).message, loading: false });
        }
      },

      loadGame: async () => {
        const { user } = get();
        if (!user.userId) return;
        set({ loading: true, error: null });
        try {
          const response = await api.loadGame(user.userId);
          if (response.success && response.game_state) {
            const gameState = api.transformLoadedGameState(response.game_state);
            set({ gameState, loading: false });
          } else {
            set({ error: 'No save found', loading: false });
          }
        } catch (e) {
          set({ error: (e as Error).message, loading: false });
        }
      },

      deleteSave: async () => {
        const { user } = get();
        if (!user.userId) return;
        set({ loading: true, error: null });
        try {
          await api.deleteSave(user.userId);
          set({ user: { ...user, hasSave: false }, loading: false });
        } catch (e) {
          set({ error: (e as Error).message, loading: false });
        }
      },

      refreshSaveInfo: async () => {
        const { user } = get();
        if (!user.userId) return;
        try {
          const info = await api.getSaveInfo(user.userId);
          set({ user: { ...user, hasSave: info.has_save } });
        } catch (e) {
          // Ignore errors when refreshing save info
        }
      },

      // Game actions
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
    }),
    {
      name: 'rogue-game-user',
      partialize: (state) => ({ user: state.user }),
    }
  )
);
