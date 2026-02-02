import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface DamageNumberProps {
  id: string;
  amount: number;
  type: 'damage' | 'heal' | 'block' | 'energy' | 'poison';
  x: number;
  y: number;
  onComplete: (id: string) => void;
}

const getColor = (type: DamageNumberProps['type']): string => {
  switch (type) {
    case 'damage':
      return '#ef4444'; // red
    case 'heal':
      return '#22c55e'; // green
    case 'block':
      return '#3b82f6'; // blue
    case 'energy':
      return '#fbbf24'; // yellow
    case 'poison':
      return '#a855f7'; // purple
    default:
      return '#ffffff';
  }
};

const getPrefix = (type: DamageNumberProps['type']): string => {
  switch (type) {
    case 'damage':
      return '-';
    case 'heal':
      return '+';
    case 'block':
      return '+';
    case 'energy':
      return '+';
    case 'poison':
      return '-';
    default:
      return '';
  }
};

const getIcon = (type: DamageNumberProps['type']): string => {
  switch (type) {
    case 'damage':
      return '💥';
    case 'heal':
      return '❤️';
    case 'block':
      return '🛡️';
    case 'energy':
      return '⚡';
    case 'poison':
      return '☠️';
    default:
      return '';
  }
};

export const DamageNumber: React.FC<DamageNumberProps> = ({
  id,
  amount,
  type,
  x,
  y,
  onComplete,
}) => {
  const color = getColor(type);
  const prefix = getPrefix(type);
  const icon = getIcon(type);

  return (
    <motion.div
      className="damage-number"
      initial={{
        x,
        y,
        scale: 0.5,
        opacity: 0,
      }}
      animate={{
        y: y - 80,
        scale: [0.5, 1.5, 1.2],
        opacity: [0, 1, 1, 0],
      }}
      transition={{
        duration: 1.2,
        times: [0, 0.2, 0.5, 1],
        ease: 'easeOut',
      }}
      onAnimationComplete={() => onComplete(id)}
      style={{
        position: 'fixed',
        color,
        fontSize: '2rem',
        fontWeight: 'bold',
        textShadow: `0 0 10px ${color}, 0 0 20px ${color}50, 2px 2px 4px rgba(0,0,0,0.8)`,
        pointerEvents: 'none',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        gap: '0.25rem',
      }}
    >
      <span>{icon}</span>
      <span>{prefix}{amount}</span>
    </motion.div>
  );
};

// Manager component to handle multiple damage numbers
interface DamageNumberData {
  id: string;
  amount: number;
  type: 'damage' | 'heal' | 'block' | 'energy' | 'poison';
  x: number;
  y: number;
}

interface DamageNumberManagerProps {
  numbers: DamageNumberData[];
  onRemove: (id: string) => void;
}

export const DamageNumberManager: React.FC<DamageNumberManagerProps> = ({
  numbers,
  onRemove,
}) => {
  return (
    <AnimatePresence>
      {numbers.map((num) => (
        <DamageNumber
          key={num.id}
          id={num.id}
          amount={num.amount}
          type={num.type}
          x={num.x}
          y={num.y}
          onComplete={onRemove}
        />
      ))}
    </AnimatePresence>
  );
};

// Hook to manage damage numbers
export const useDamageNumbers = () => {
  const [numbers, setNumbers] = React.useState<DamageNumberData[]>([]);
  let idCounter = React.useRef(0);

  const addDamageNumber = (
    amount: number,
    type: DamageNumberData['type'],
    x: number,
    y: number
  ) => {
    const id = `damage-${idCounter.current++}`;
    // Add slight random offset for visual variety
    const offsetX = x + (Math.random() - 0.5) * 40;
    const offsetY = y + (Math.random() - 0.5) * 20;

    setNumbers(prev => [...prev, { id, amount, type, x: offsetX, y: offsetY }]);
  };

  const removeDamageNumber = (id: string) => {
    setNumbers(prev => prev.filter(n => n.id !== id));
  };

  return {
    numbers,
    addDamageNumber,
    removeDamageNumber,
    DamageNumberManager: () => (
      <DamageNumberManager numbers={numbers} onRemove={removeDamageNumber} />
    ),
  };
};

export default DamageNumber;
