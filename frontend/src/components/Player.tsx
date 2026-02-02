import React from 'react';
import type { Player as PlayerType } from '../types';
import '../styles/combat.css';

interface PlayerProps {
  player: PlayerType;
}

const getStatusEffectInfo = (effectName: string): { icon: string; color: string; description: string } => {
  const effects: Record<string, { icon: string; color: string; description: string }> = {
    vulnerable: { icon: '💥', color: '#ef4444', description: 'Take 50% more damage from attacks' },
    weak: { icon: '📉', color: '#f97316', description: 'Deal 25% less attack damage' },
    frail: { icon: '🦴', color: '#a855f7', description: 'Gain 25% less block' },
    strength: { icon: '💪', color: '#22c55e', description: 'Deal additional damage with attacks' },
    dexterity: { icon: '🏃', color: '#3b82f6', description: 'Gain additional block' },
    artifact: { icon: '🏺', color: '#f59e0b', description: 'Negate debuff applications' },
    intangible: { icon: '👻', color: '#8b5cf6', description: 'Reduce all damage to 1' },
    metallicize: { icon: '🔩', color: '#6b7280', description: 'Gain block at end of turn' },
    plated_armor: { icon: '🛡️', color: '#9ca3af', description: 'Gain block at end of turn' },
    thorns: { icon: '🌹', color: '#dc2626', description: 'Deal damage when attacked' },
    regen: { icon: '💚', color: '#10b981', description: 'Heal at end of turn' },
    barricade: { icon: '🏰', color: '#78716c', description: 'Block is not removed at start of turn' },
  };

  return effects[effectName.toLowerCase()] || { icon: '❔', color: '#6b7280', description: effectName };
};

export const Player: React.FC<PlayerProps> = ({ player }) => {
  const hpPercent = (player.currentHp / player.maxHp) * 100;
  const statusEntries = Object.entries(player.statusEffects);

  // Determine HP bar color based on percentage
  const getHpColor = (): string => {
    if (hpPercent > 50) return '#22c55e'; // green
    if (hpPercent > 25) return '#f59e0b'; // yellow/orange
    return '#ef4444'; // red
  };

  // Generate energy orbs
  const energyOrbs = [];
  for (let i = 0; i < player.maxEnergy; i++) {
    energyOrbs.push(
      <div
        key={i}
        className={`energy-orb ${i < player.energy ? 'energy-filled' : 'energy-empty'}`}
      >
        {i < player.energy && <span className="energy-glow" />}
      </div>
    );
  }

  return (
    <div className="player-container">
      {/* Player portrait/sprite */}
      <div className="player-portrait">
        <div className="player-sprite">🧙</div>
      </div>

      {/* Player info panel */}
      <div className="player-info">
        {/* Player name */}
        <div className="player-name">{player.name}</div>

        {/* HP Bar */}
        <div className="player-hp-container">
          <div className="player-hp-bar">
            <div
              className="player-hp-fill"
              style={{
                width: `${hpPercent}%`,
                backgroundColor: getHpColor(),
              }}
            />
            <div className="player-hp-text">
              <span className="hp-icon">❤️</span>
              {player.currentHp} / {player.maxHp}
            </div>
          </div>
        </div>

        {/* Block display */}
        {player.block > 0 && (
          <div className="player-block">
            <span className="block-shield">🛡️</span>
            <span className="block-value">{player.block}</span>
          </div>
        )}

        {/* Energy display */}
        <div className="player-energy">
          <div className="energy-orbs">{energyOrbs}</div>
          <div className="energy-text">
            {player.energy} / {player.maxEnergy}
          </div>
        </div>

        {/* Status effects */}
        {statusEntries.length > 0 && (
          <div className="player-status-effects">
            {statusEntries.map(([name, value]) => {
              const info = getStatusEffectInfo(name);
              return (
                <div
                  key={name}
                  className="status-effect"
                  style={{ borderColor: info.color }}
                  title={`${name}: ${info.description}`}
                >
                  <span className="status-icon">{info.icon}</span>
                  <span className="status-value" style={{ color: info.color }}>{value}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Player;
