import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence, useAnimation } from 'framer-motion';
import type { Enemy as EnemyType, IntentType } from '../types';
import '../styles/combat.css';

interface EnemyProps {
  enemy: EnemyType;
  isTargetable: boolean;
  onTarget: () => void;
  isDamaged?: boolean;
}

const getIntentIcon = (intentType: IntentType): string => {
  switch (intentType) {
    case 'attack':
      return '⚔️';
    case 'defend':
      return '🛡️';
    case 'buff':
      return '💪';
    case 'debuff':
      return '💔';
    case 'attack_defend':
      return '⚔️🛡️';
    case 'attack_buff':
      return '⚔️💪';
    case 'attack_debuff':
      return '⚔️💔';
    case 'sleeping':
      return '💤';
    case 'unknown':
    default:
      return '❓';
  }
};

const getIntentText = (intent: EnemyType['intent']): string => {
  const { intentType, damage, times, block } = intent;

  let text = '';

  if (damage !== null) {
    text += `${damage}`;
    if (times > 1) {
      text += ` x${times}`;
    }
  }

  if (block !== null) {
    if (text) text += ' + ';
    text += `${block} Block`;
  }

  if (!text) {
    switch (intentType) {
      case 'buff':
        return 'Buffing';
      case 'debuff':
        return 'Debuffing';
      case 'sleeping':
        return 'Sleeping';
      case 'unknown':
        return '???';
      default:
        return '';
    }
  }

  return text;
};

const getStatusEffectInfo = (effectName: string): { icon: string; color: string; description: string } => {
  const effects: Record<string, { icon: string; color: string; description: string }> = {
    vulnerable: { icon: '💥', color: '#ef4444', description: 'Take 50% more damage from attacks' },
    weak: { icon: '📉', color: '#f97316', description: 'Deal 25% less attack damage' },
    frail: { icon: '🦴', color: '#a855f7', description: 'Gain 25% less block' },
    strength: { icon: '💪', color: '#22c55e', description: 'Deal additional damage with attacks' },
    dexterity: { icon: '🏃', color: '#3b82f6', description: 'Gain additional block' },
    poison: { icon: '☠️', color: '#84cc16', description: 'Take damage at start of turn' },
    ritual: { icon: '🔮', color: '#8b5cf6', description: 'Gain strength at end of turn' },
    thorns: { icon: '🌹', color: '#dc2626', description: 'Deal damage when attacked' },
    regen: { icon: '💚', color: '#10b981', description: 'Heal at end of turn' },
  };

  return effects[effectName.toLowerCase()] || { icon: '❔', color: '#6b7280', description: effectName };
};

export const Enemy: React.FC<EnemyProps> = ({
  enemy,
  isTargetable,
  onTarget,
  isDamaged = false,
}) => {
  const hpPercent = (enemy.currentHp / enemy.maxHp) * 100;
  const statusEntries = Object.entries(enemy.statusEffects);
  const controls = useAnimation();
  const [prevHp, setPrevHp] = useState(enemy.currentHp);
  const [showDamageFlash, setShowDamageFlash] = useState(false);

  // Shake animation when damaged
  useEffect(() => {
    if (enemy.currentHp < prevHp) {
      setShowDamageFlash(true);
      controls.start({
        x: [0, -10, 10, -10, 10, -5, 5, 0],
        transition: { duration: 0.4 }
      });
      setTimeout(() => setShowDamageFlash(false), 200);
    }
    setPrevHp(enemy.currentHp);
  }, [enemy.currentHp, controls, prevHp]);

  // Animation variants
  const enemyVariants = {
    initial: {
      scale: 0,
      opacity: 0,
      y: -50,
    },
    animate: {
      scale: 1,
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 200,
        damping: 20,
      }
    },
    exit: {
      scale: 0,
      opacity: 0,
      y: 50,
      rotate: 10,
      transition: {
        duration: 0.5,
        ease: 'easeIn',
      }
    },
    hover: isTargetable ? {
      scale: 1.05,
      transition: {
        type: 'spring',
        stiffness: 400,
        damping: 20,
      }
    } : {},
    tap: isTargetable ? {
      scale: 0.95,
    } : {},
  };

  const intentVariants = {
    initial: { y: -20, opacity: 0 },
    animate: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 25,
      }
    },
    pulse: {
      scale: [1, 1.1, 1],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeInOut',
      }
    }
  };

  const blockVariants = {
    initial: { scale: 0, opacity: 0 },
    animate: {
      scale: 1,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 500,
        damping: 20,
      }
    },
    exit: {
      scale: 0,
      opacity: 0,
      transition: { duration: 0.2 }
    }
  };

  return (
    <motion.div
      className={`enemy ${isTargetable ? 'enemy-targetable' : ''} ${isDamaged || showDamageFlash ? 'enemy-damaged' : ''}`}
      onClick={isTargetable ? onTarget : undefined}
      variants={enemyVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      whileHover="hover"
      whileTap="tap"
      layoutId={`enemy-${enemy.id}`}
    >
      {/* Damage flash overlay */}
      <AnimatePresence>
        {showDamageFlash && (
          <motion.div
            className="damage-flash-overlay"
            initial={{ opacity: 0.8 }}
            animate={{ opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            style={{
              position: 'absolute',
              inset: 0,
              backgroundColor: '#ef4444',
              borderRadius: 'inherit',
              pointerEvents: 'none',
              zIndex: 10,
            }}
          />
        )}
      </AnimatePresence>

      {/* Intent display */}
      <motion.div
        className="enemy-intent"
        variants={intentVariants}
        initial="initial"
        animate={['animate', 'pulse']}
        key={`${enemy.intent.intentType}-${enemy.intent.damage}`}
      >
        <motion.span
          className="intent-icon"
          animate={{
            y: [0, -3, 0],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          {getIntentIcon(enemy.intent.intentType)}
        </motion.span>
        <span className="intent-text">{getIntentText(enemy.intent)}</span>
      </motion.div>

      {/* Enemy name */}
      <motion.div
        className="enemy-name"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        {enemy.name}
      </motion.div>

      {/* Enemy sprite placeholder */}
      <motion.div
        className="enemy-sprite"
        animate={controls}
      >
        <motion.div
          className="enemy-sprite-placeholder"
          animate={{
            y: [0, -5, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          👹
        </motion.div>
      </motion.div>

      {/* HP Bar */}
      <div className="enemy-hp-container">
        <div className="enemy-hp-bar">
          <motion.div
            className="enemy-hp-fill"
            initial={{ width: '100%' }}
            animate={{ width: `${hpPercent}%` }}
            transition={{
              type: 'spring',
              stiffness: 100,
              damping: 15,
            }}
            style={{
              backgroundColor: hpPercent > 50 ? '#ef4444' : hpPercent > 25 ? '#f97316' : '#dc2626',
            }}
          />
          <motion.div
            className="enemy-hp-text"
            key={enemy.currentHp}
            initial={{ scale: 1.2 }}
            animate={{ scale: 1 }}
          >
            {enemy.currentHp} / {enemy.maxHp}
          </motion.div>
        </div>

        {/* Block shield */}
        <AnimatePresence>
          {enemy.block > 0 && (
            <motion.div
              className="enemy-block"
              variants={blockVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <motion.span
                className="block-icon"
                animate={{ rotate: [0, -10, 10, 0] }}
                transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
              >
                🛡️
              </motion.span>
              <motion.span
                className="block-value"
                key={enemy.block}
                initial={{ scale: 1.5 }}
                animate={{ scale: 1 }}
              >
                {enemy.block}
              </motion.span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Status effects */}
      {statusEntries.length > 0 && (
        <motion.div
          className="enemy-status-effects"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <AnimatePresence>
            {statusEntries.map(([name, value], index) => {
              const info = getStatusEffectInfo(name);
              return (
                <motion.div
                  key={name}
                  className="status-effect"
                  style={{ borderColor: info.color }}
                  title={`${name}: ${info.description}`}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <span className="status-icon">{info.icon}</span>
                  <motion.span
                    className="status-value"
                    style={{ color: info.color }}
                    key={`${name}-${value}`}
                    initial={{ scale: 1.3 }}
                    animate={{ scale: 1 }}
                  >
                    {value}
                  </motion.span>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Targeting indicator */}
      <AnimatePresence>
        {isTargetable && (
          <motion.div
            className="enemy-target-indicator"
            initial={{ scale: 0, opacity: 0 }}
            animate={{
              scale: [1, 1.2, 1],
              opacity: 1,
            }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{
              scale: {
                duration: 0.8,
                repeat: Infinity,
                ease: 'easeInOut',
              }
            }}
          >
            <span className="target-icon">🎯</span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default Enemy;
