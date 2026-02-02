import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Card as CardType } from '../types';
import Card from './Card';
import '../styles/combat.css';

interface HandProps {
  cards: CardType[];
  selectedIndex: number | null;
  onCardClick: (index: number) => void;
  disabled: boolean;
}

export const Hand: React.FC<HandProps> = ({
  cards,
  selectedIndex,
  onCardClick,
  disabled,
}) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [prevCardIds, setPrevCardIds] = useState<Set<string>>(new Set());
  const [newCardIds, setNewCardIds] = useState<Set<string>>(new Set());

  // Track which cards are new (for draw animation)
  useEffect(() => {
    const currentIds = new Set(cards.map(c => c.id));
    const newIds = new Set<string>();

    cards.forEach(card => {
      if (!prevCardIds.has(card.id)) {
        newIds.add(card.id);
      }
    });

    setNewCardIds(newIds);
    setPrevCardIds(currentIds);

    // Clear new card status after animation
    if (newIds.size > 0) {
      const timer = setTimeout(() => {
        setNewCardIds(new Set());
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [cards]);

  const getCardTransform = (index: number, total: number) => {
    if (total === 0) return { x: 0, y: 0, rotate: 0 };

    const center = (total - 1) / 2;
    const offset = index - center;

    // Arc calculation - middle cards are higher
    const maxRotation = Math.min(15, 30 / total);
    const rotation = offset * maxRotation;

    // Vertical offset for arc effect
    const normalizedOffset = offset / Math.max(center, 1);
    const verticalOffset = Math.abs(normalizedOffset) * 40;

    // Horizontal positioning
    const cardWidth = 140;
    const overlap = Math.max(0.3, 1 - (total * 0.05));
    const spacing = cardWidth * overlap;
    const totalWidth = spacing * (total - 1);
    const startX = -totalWidth / 2;
    const horizontalPos = startX + (index * spacing);

    // Spread adjacent cards when hovering
    let spreadOffset = 0;
    if (hoveredIndex !== null && hoveredIndex !== index) {
      const distFromHovered = index - hoveredIndex;
      if (Math.abs(distFromHovered) === 1) {
        spreadOffset = distFromHovered * 40;
      } else if (Math.abs(distFromHovered) === 2) {
        spreadOffset = distFromHovered * 15;
      }
    }

    // Lift hovered card
    const isHovered = hoveredIndex === index;
    const hoverLift = isHovered ? -80 : 0;
    const hoverRotation = isHovered ? 0 : rotation;

    // Selected card lift
    const isSelected = selectedIndex === index;
    const selectedLift = isSelected && !isHovered ? -40 : 0;

    return {
      x: horizontalPos + spreadOffset,
      y: verticalOffset + hoverLift + selectedLift,
      rotate: hoverRotation,
      scale: isHovered ? 1.2 : isSelected ? 1.1 : 1,
      zIndex: isHovered ? 100 : isSelected ? 50 : total - Math.abs(offset) * 2,
    };
  };

  // Container animation
  const containerVariants = {
    hidden: { opacity: 0, y: 100 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.4,
        staggerChildren: 0.05,
      }
    },
  };

  return (
    <motion.div
      className="hand-container"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="hand">
        <AnimatePresence mode="popLayout">
          {cards.map((card, index) => {
            const transform = getCardTransform(index, cards.length);
            const isNew = newCardIds.has(card.id);

            return (
              <motion.div
                key={card.id}
                className="hand-card-wrapper"
                initial={isNew ? {
                  x: -400,
                  y: -300,
                  rotate: -45,
                  scale: 0.3,
                  opacity: 0
                } : false}
                animate={{
                  x: transform.x,
                  y: transform.y,
                  rotate: transform.rotate,
                  scale: transform.scale,
                  opacity: 1,
                }}
                exit={{
                  x: transform.x + 400,
                  y: 300,
                  rotate: 45,
                  scale: 0.3,
                  opacity: 0,
                  transition: { duration: 0.3, ease: 'easeIn' }
                }}
                transition={{
                  type: 'spring',
                  stiffness: 300,
                  damping: 25,
                  delay: isNew ? index * 0.1 : 0,
                }}
                style={{ zIndex: transform.zIndex }}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                layout
              >
                <Card
                  card={card}
                  selected={selectedIndex === index}
                  onClick={() => onCardClick(index)}
                  disabled={disabled}
                  isNew={isNew}
                />
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Draw pile indicator */}
      <motion.div
        className="draw-pile-indicator"
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3 }}
      >
        📚 Draw
      </motion.div>

      {/* Discard pile indicator */}
      <motion.div
        className="discard-pile-indicator"
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3 }}
      >
        Discard 📚
      </motion.div>

      {/* Card count indicator */}
      <motion.div
        className="hand-count"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <motion.span
          key={cards.length}
          initial={{ scale: 1.5, color: '#fbbf24' }}
          animate={{ scale: 1, color: '#9ca3af' }}
          transition={{ duration: 0.3 }}
        >
          {cards.length}
        </motion.span>
        {' '}cards in hand
      </motion.div>
    </motion.div>
  );
};

export default Hand;
