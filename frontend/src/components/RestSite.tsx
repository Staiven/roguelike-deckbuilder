import { useState } from 'react';
import { useGameStore } from '../store/gameStore';
import type { Card } from '../types';
import './RestSite.css';

export function RestSite() {
  const { gameState, restHeal, restUpgrade, loading } = useGameStore();
  const [mode, setMode] = useState<'choose' | 'upgrade'>('choose');

  if (!gameState) return null;

  const { player } = gameState;
  const healAmount = Math.floor(player.maxHp * 0.3);
  const healedHp = Math.min(player.currentHp + healAmount, player.maxHp);
  const actualHeal = healedHp - player.currentHp;

  // For demo purposes, we'll create a mock deck since we don't have it in state
  // In a real implementation, this would come from the game state
  const mockDeck: Card[] = [
    { id: '1', name: 'Strike', cost: 1, cardType: 'attack', targetType: 'single_enemy', rarity: 'starter', description: 'Deal 6 damage.', upgraded: false, exhaust: false, ethereal: false },
    { id: '2', name: 'Defend', cost: 1, cardType: 'skill', targetType: 'self', rarity: 'starter', description: 'Gain 5 block.', upgraded: false, exhaust: false, ethereal: false },
    { id: '3', name: 'Bash', cost: 2, cardType: 'attack', targetType: 'single_enemy', rarity: 'starter', description: 'Deal 8 damage. Apply 2 Vulnerable.', upgraded: false, exhaust: false, ethereal: false },
  ];

  const handleRest = () => {
    if (!loading) {
      restHeal();
    }
  };

  const handleSmith = () => {
    setMode('upgrade');
  };

  const handleUpgradeCard = (cardIndex: number) => {
    if (!loading) {
      restUpgrade(cardIndex);
    }
  };

  const handleBackToChoose = () => {
    setMode('choose');
  };

  return (
    <div className="rest-site">
      <div className="rest-site__glow"></div>
      <div className="rest-site__campfire">
        <div className="campfire__flames">
          <div className="flame flame--1"></div>
          <div className="flame flame--2"></div>
          <div className="flame flame--3"></div>
        </div>
        <div className="campfire__logs"></div>
      </div>

      <div className="rest-site__content">
        {mode === 'choose' ? (
          <>
            <h1 className="rest-site__title">Rest Site</h1>
            <p className="rest-site__subtitle">Take a moment to recover...</p>

            <div className="rest-site__options">
              <button
                className="rest-option rest-option--heal"
                onClick={handleRest}
                disabled={loading || player.currentHp === player.maxHp}
              >
                <div className="rest-option__icon">❤️</div>
                <div className="rest-option__name">Rest</div>
                <div className="rest-option__description">
                  Heal {actualHeal > 0 ? actualHeal : 0} HP (30% max HP)
                </div>
                <div className="rest-option__current">
                  {player.currentHp}/{player.maxHp} HP
                </div>
              </button>

              <button
                className="rest-option rest-option--smith"
                onClick={handleSmith}
                disabled={loading}
              >
                <div className="rest-option__icon">⚒️</div>
                <div className="rest-option__name">Smith</div>
                <div className="rest-option__description">
                  Upgrade a card
                </div>
              </button>
            </div>
          </>
        ) : (
          <>
            <h1 className="rest-site__title">Upgrade a Card</h1>
            <p className="rest-site__subtitle">Choose a card to improve</p>

            <div className="rest-site__deck">
              {mockDeck.filter(card => !card.upgraded).map((card, index) => (
                <button
                  key={card.id}
                  className={`upgrade-card upgrade-card--${card.cardType}`}
                  onClick={() => handleUpgradeCard(index)}
                  disabled={loading}
                >
                  <div className="upgrade-card__cost">{card.cost}</div>
                  <div className="upgrade-card__name">{card.name}</div>
                  <div className="upgrade-card__type">{card.cardType}</div>
                  <div className="upgrade-card__description">{card.description}</div>
                </button>
              ))}
            </div>

            <button
              className="rest-site__back"
              onClick={handleBackToChoose}
              disabled={loading}
            >
              Back
            </button>
          </>
        )}
      </div>

      {loading && <div className="rest-site__loading">Processing...</div>}
    </div>
  );
}
