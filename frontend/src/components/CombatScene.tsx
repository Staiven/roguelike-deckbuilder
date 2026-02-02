import React, { useState, useCallback, useMemo } from 'react';
import { useGameStore } from '../store/gameStore';
import type { Card as CardType } from '../types';
import Hand from './Hand';
import Enemy from './Enemy';
import Player from './Player';
import '../styles/combat.css';

export const CombatScene: React.FC = () => {
  const { gameState, selectedCard, selectCard, playCard, endTurn, loading } = useGameStore();
  const [damagedEnemies, setDamagedEnemies] = useState<Set<string>>(new Set());

  const combat = gameState?.combat;
  const player = combat?.player;
  const enemies = combat?.enemies || [];
  const hand = combat?.hand || [];
  const isPlayerTurn = combat?.phase === 'player_turn';

  // Get the selected card data
  const selectedCardData: CardType | null = useMemo(() => {
    if (selectedCard === null || selectedCard >= hand.length) return null;
    return hand[selectedCard];
  }, [selectedCard, hand]);

  // Determine if we need to select a target
  const needsTarget = useMemo((): boolean => {
    if (!selectedCardData) return false;
    return selectedCardData.targetType === 'single_enemy';
  }, [selectedCardData]);

  // Check if player has enough energy
  const hasEnoughEnergy = useCallback((card: CardType): boolean => {
    if (!player) return false;
    return player.energy >= card.cost;
  }, [player]);

  // Handle card click
  const handleCardClick = useCallback((index: number) => {
    if (!isPlayerTurn || loading) return;

    const card = hand[index];
    if (!hasEnoughEnergy(card)) return;

    if (selectedCard === index) {
      // Clicking already selected card - deselect or play if no target needed
      if (card.targetType === 'self' || card.targetType === 'all_enemies' || card.targetType === 'none') {
        playCard(index);
      } else {
        selectCard(null);
      }
    } else {
      // Select the card
      selectCard(index);

      // Auto-play if doesn't need target
      if (card.targetType === 'self' || card.targetType === 'all_enemies' || card.targetType === 'none') {
        playCard(index);
      }
    }
  }, [isPlayerTurn, loading, hand, selectedCard, hasEnoughEnergy, selectCard, playCard]);

  // Handle enemy targeting
  const handleEnemyTarget = useCallback((enemyIndex: number) => {
    if (!needsTarget || selectedCard === null || loading) return;

    // Trigger damage animation
    const enemy = enemies[enemyIndex];
    setDamagedEnemies(prev => new Set(prev).add(enemy.id));
    setTimeout(() => {
      setDamagedEnemies(prev => {
        const next = new Set(prev);
        next.delete(enemy.id);
        return next;
      });
    }, 500);

    playCard(selectedCard, enemyIndex);
  }, [needsTarget, selectedCard, enemies, loading, playCard]);

  // Handle end turn
  const handleEndTurn = useCallback(() => {
    if (!isPlayerTurn || loading) return;
    selectCard(null);
    endTurn();
  }, [isPlayerTurn, loading, selectCard, endTurn]);

  // Cancel card selection
  const handleCancel = useCallback(() => {
    selectCard(null);
  }, [selectCard]);

  if (!combat || !player) {
    return (
      <div className="combat-scene combat-loading">
        <div className="loading-spinner">Loading combat...</div>
      </div>
    );
  }

  return (
    <div className="combat-scene">
      {/* Background */}
      <div className="combat-background">
        <div className="combat-bg-overlay" />
      </div>

      {/* Turn indicator */}
      <div className="turn-indicator">
        <span className="turn-number">Turn {combat.turn}</span>
        <span className={`turn-phase ${combat.phase}`}>
          {combat.phase === 'player_turn' ? 'Your Turn' :
           combat.phase === 'enemy_turn' ? 'Enemy Turn' :
           combat.result === 'victory' ? 'Victory!' :
           combat.result === 'defeat' ? 'Defeat' : ''}
        </span>
      </div>

      {/* Enemies area */}
      <div className="enemies-container">
        {enemies.map((enemy, index) => (
          <Enemy
            key={enemy.id}
            enemy={enemy}
            isTargetable={needsTarget && isPlayerTurn}
            onTarget={() => handleEnemyTarget(index)}
            isDamaged={damagedEnemies.has(enemy.id)}
          />
        ))}
      </div>

      {/* Player area */}
      <div className="player-area">
        <Player player={player} />
      </div>

      {/* Deck info */}
      <div className="deck-info">
        <div className="deck-pile draw-pile" title="Draw Pile">
          <span className="pile-icon">📚</span>
          <span className="pile-count">{combat.drawPileCount}</span>
        </div>
        <div className="deck-pile discard-pile" title="Discard Pile">
          <span className="pile-icon">🗑️</span>
          <span className="pile-count">{combat.discardPileCount}</span>
        </div>
        {combat.exhaustPileCount > 0 && (
          <div className="deck-pile exhaust-pile" title="Exhaust Pile">
            <span className="pile-icon">🔥</span>
            <span className="pile-count">{combat.exhaustPileCount}</span>
          </div>
        )}
      </div>

      {/* Hand area */}
      <div className="hand-area">
        <Hand
          cards={hand}
          selectedIndex={selectedCard}
          onCardClick={handleCardClick}
          disabled={!isPlayerTurn || loading}
        />
      </div>

      {/* Action buttons */}
      <div className="combat-actions">
        {selectedCard !== null && needsTarget && (
          <button
            className="action-button cancel-button"
            onClick={handleCancel}
          >
            Cancel
          </button>
        )}
        <button
          className={`action-button end-turn-button ${!isPlayerTurn || loading ? 'disabled' : ''}`}
          onClick={handleEndTurn}
          disabled={!isPlayerTurn || loading}
        >
          {loading ? 'Processing...' : 'End Turn'}
        </button>
      </div>

      {/* Energy display (large) */}
      <div className="combat-energy">
        <div className="energy-orb-large">
          <span className="energy-current">{player.energy}</span>
          <span className="energy-divider">/</span>
          <span className="energy-max">{player.maxEnergy}</span>
        </div>
        <div className="energy-label">Energy</div>
      </div>

      {/* Targeting overlay */}
      {needsTarget && (
        <div className="targeting-overlay">
          <div className="targeting-message">
            Select a target for {selectedCardData?.name}
          </div>
        </div>
      )}

      {/* Combat result overlay */}
      {combat.result !== 'in_progress' && (
        <div className={`combat-result-overlay ${combat.result}`}>
          <div className="result-content">
            <h2 className="result-title">
              {combat.result === 'victory' ? '🎉 Victory! 🎉' : '💀 Defeat 💀'}
            </h2>
            <p className="result-message">
              {combat.result === 'victory'
                ? 'You have defeated all enemies!'
                : 'You have been defeated...'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default CombatScene;
