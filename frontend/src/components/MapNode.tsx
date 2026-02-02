import { motion } from 'framer-motion';
import type { MapNodeType, MapNode as MapNodeData } from '../types';
import '../styles/map.css';

// Icon mapping for node types
const nodeIcons: Record<MapNodeType, string> = {
  combat: '\u2694\uFE0F',    // Crossed swords
  elite: '\uD83D\uDC80',     // Skull
  rest: '\uD83D\uDD25',      // Fire/campfire
  shop: '\uD83D\uDCB0',      // Money bag
  event: '\u2753',           // Question mark
  boss: '\uD83D\uDC79',      // Boss face (ogre)
  treasure: '\uD83D\uDC8E',  // Gem
};

// Color mapping for node types
const nodeColors: Record<MapNodeType, string> = {
  combat: '#e74c3c',    // Red
  elite: '#9b59b6',     // Purple
  rest: '#27ae60',      // Green
  shop: '#f1c40f',      // Yellow
  event: '#3498db',     // Blue
  boss: '#c0392b',      // Dark red
  treasure: '#f39c12',  // Orange
};

interface MapNodeProps {
  node: MapNodeData;
  isCurrent: boolean;
  onClick: (row: number, col: number) => void;
}

export function MapNode({ node, isCurrent, onClick }: MapNodeProps) {
  const { row, col, nodeType, visited, available } = node;

  const getNodeClass = (): string => {
    const classes = ['map-node'];

    if (isCurrent) {
      classes.push('map-node--current');
    } else if (available) {
      classes.push('map-node--available');
    } else if (visited) {
      classes.push('map-node--visited');
    } else {
      classes.push('map-node--locked');
    }

    classes.push(`map-node--${nodeType}`);

    return classes.join(' ');
  };

  const handleClick = () => {
    if (available && !isCurrent) {
      onClick(row, col);
    }
  };

  return (
    <motion.div
      className={getNodeClass()}
      onClick={handleClick}
      style={{
        '--node-color': nodeColors[nodeType],
      } as React.CSSProperties}
      whileHover={available && !isCurrent ? {
        scale: 1.15,
        transition: { duration: 0.2 }
      } : {}}
      whileTap={available && !isCurrent ? {
        scale: 0.95
      } : {}}
      initial={{ opacity: 0, scale: 0 }}
      animate={{
        opacity: 1,
        scale: 1,
        transition: {
          delay: row * 0.05 + col * 0.02,
          duration: 0.3,
          type: 'spring',
          stiffness: 200
        }
      }}
      aria-label={`${nodeType} node at row ${row}, column ${col}${available ? ' - available' : ''}${visited ? ' - visited' : ''}`}
      role="button"
      tabIndex={available && !isCurrent ? 0 : -1}
      onKeyDown={(e) => {
        if ((e.key === 'Enter' || e.key === ' ') && available && !isCurrent) {
          handleClick();
        }
      }}
    >
      <div className="map-node__icon">
        {nodeIcons[nodeType]}
      </div>

      {isCurrent && (
        <motion.div
          className="map-node__current-indicator"
          initial={{ scale: 0 }}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{
            repeat: Infinity,
            duration: 1.5,
            ease: 'easeInOut'
          }}
        />
      )}

      {available && !isCurrent && (
        <motion.div
          className="map-node__glow"
          animate={{
            opacity: [0.5, 1, 0.5],
            scale: [1, 1.1, 1],
          }}
          transition={{
            repeat: Infinity,
            duration: 2,
            ease: 'easeInOut'
          }}
        />
      )}
    </motion.div>
  );
}

export default MapNode;
