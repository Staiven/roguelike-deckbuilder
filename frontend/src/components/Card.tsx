import React from 'react';
import { motion } from 'framer-motion';
import type { Card as CardType } from '../types';
import '../styles/combat.css';

interface CardProps {
  card: CardType;
  selected: boolean;
  onClick: () => void;
  disabled: boolean;
  style?: React.CSSProperties;
  isNew?: boolean; // For draw animation
  layoutId?: string; // For shared layout animations
}

const getBorderColor = (cardType: CardType['cardType']): string => {
  switch (cardType) {
    case 'attack':
      return '#dc2626'; // red
    case 'skill':
      return '#2563eb'; // blue
    case 'power':
      return '#eab308'; // yellow
    case 'status':
      return '#6b7280'; // gray
    case 'curse':
      return '#7c3aed'; // purple
    default:
      return '#6b7280';
  }
};

const getCardBackground = (cardType: CardType['cardType']): string => {
  switch (cardType) {
    case 'attack':
      return 'linear-gradient(145deg, #1a0a0a 0%, #2d1515 50%, #1a0a0a 100%)';
    case 'skill':
      return 'linear-gradient(145deg, #0a0a1a 0%, #15152d 50%, #0a0a1a 100%)';
    case 'power':
      return 'linear-gradient(145deg, #1a1a0a 0%, #2d2d15 50%, #1a1a0a 100%)';
    case 'status':
      return 'linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)';
    case 'curse':
      return 'linear-gradient(145deg, #150a1a 0%, #25152d 50%, #150a1a 100%)';
    default:
      return 'linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)';
  }
};

const getTypeBadgeColor = (cardType: CardType['cardType']): string => {
  switch (cardType) {
    case 'attack':
      return '#ef4444';
    case 'skill':
      return '#3b82f6';
    case 'power':
      return '#f59e0b';
    case 'status':
      return '#9ca3af';
    case 'curse':
      return '#8b5cf6';
    default:
      return '#9ca3af';
  }
};

export const Card: React.FC<CardProps> = ({
  card,
  selected,
  onClick,
  disabled,
  style,
  isNew = false,
  layoutId,
}) => {
  const borderColor = getBorderColor(card.cardType);
  const background = getCardBackground(card.cardType);
  const badgeColor = getTypeBadgeColor(card.cardType);

  const handleClick = () => {
    if (!disabled) {
      onClick();
    }
  };

  // Animation variants
  const cardVariants = {
    initial: isNew ? {
      x: -300,
      y: -200,
      rotate: -30,
      scale: 0.5,
      opacity: 0
    } : {
      scale: 1,
      opacity: 1
    },
    animate: {
      x: 0,
      y: 0,
      rotate: 0,
      scale: 1,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 25,
      }
    },
    hover: !disabled ? {
      scale: 1.05,
      y: -10,
      boxShadow: `0 20px 40px rgba(0, 0, 0, 0.4), 0 0 20px ${borderColor}40`,
      transition: {
        type: 'spring',
        stiffness: 400,
        damping: 20,
      }
    } : {},
    tap: !disabled ? {
      scale: 0.98,
      transition: {
        type: 'spring',
        stiffness: 600,
        damping: 20,
      }
    } : {},
    selected: {
      scale: 1.08,
      y: -20,
      boxShadow: `0 25px 50px rgba(0, 0, 0, 0.5), 0 0 30px ${borderColor}60`,
    },
    exit: {
      x: 300,
      y: 200,
      rotate: 30,
      scale: 0.5,
      opacity: 0,
      transition: {
        duration: 0.3,
        ease: 'easeIn',
      }
    }
  };

  return (
    <motion.div
      className={`card ${selected ? 'card-selected' : ''} ${disabled ? 'card-disabled' : ''}`}
      onClick={handleClick}
      style={{
        ...style,
        borderColor,
        background,
        '--glow-color': borderColor,
      } as React.CSSProperties}
      variants={cardVariants}
      initial="initial"
      animate={selected ? 'selected' : 'animate'}
      whileHover="hover"
      whileTap="tap"
      exit="exit"
      layoutId={layoutId}
    >
      {/* Energy cost orb */}
      <motion.div
        className="card-cost-orb"
        whileHover={{ scale: 1.2 }}
      >
        <span className="card-cost">{card.cost}</span>
      </motion.div>

      {/* Card name */}
      <div className="card-name">
        {card.name}
        {card.upgraded && (
          <motion.span
            className="card-upgraded"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', delay: 0.2 }}
          >
            +
          </motion.span>
        )}
      </div>

      {/* Card type badge */}
      <motion.div
        className="card-type-badge"
        style={{ backgroundColor: badgeColor }}
        whileHover={{ scale: 1.1 }}
      >
        {card.cardType.charAt(0).toUpperCase() + card.cardType.slice(1)}
      </motion.div>

      {/* Card art placeholder */}
      <div className="card-art">
        <motion.div
          className="card-art-icon"
          animate={{
            rotate: [0, 5, -5, 0],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        >
          {card.cardType === 'attack' && '⚔️'}
          {card.cardType === 'skill' && '🛡️'}
          {card.cardType === 'power' && '⚡'}
          {card.cardType === 'status' && '📋'}
          {card.cardType === 'curse' && '💀'}
        </motion.div>
      </div>

      {/* Description */}
      <div className="card-description">
        {card.description}
      </div>

      {/* Keywords */}
      <div className="card-keywords">
        {card.exhaust && (
          <motion.span
            className="card-keyword exhaust"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
          >
            Exhaust
          </motion.span>
        )}
        {card.ethereal && (
          <motion.span
            className="card-keyword ethereal"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
          >
            Ethereal
          </motion.span>
        )}
      </div>

      {/* Rarity indicator */}
      <motion.div
        className={`card-rarity rarity-${card.rarity}`}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay: 0.3, duration: 0.3 }}
      />

      {/* Hover tooltip */}
      <div className="card-tooltip">
        <div className="tooltip-header">
          <span className="tooltip-name">{card.name}</span>
          <span className="tooltip-cost">Cost: {card.cost}</span>
        </div>
        <div className="tooltip-type">Type: {card.cardType}</div>
        <div className="tooltip-target">Target: {card.targetType.replace('_', ' ')}</div>
        <div className="tooltip-description">{card.description}</div>
        {card.exhaust && <div className="tooltip-keyword">Exhaust: This card is removed from combat after playing.</div>}
        {card.ethereal && <div className="tooltip-keyword">Ethereal: This card is exhausted if still in hand at end of turn.</div>}
      </div>
    </motion.div>
  );
};

export default Card;
