import { motion } from 'framer-motion';
import '../styles/map.css';

interface Position {
  x: number;
  y: number;
}

interface MapConnectionProps {
  from: Position;
  to: Position;
  visited: boolean;
  index?: number;
}

export function MapConnection({ from, to, visited, index = 0 }: MapConnectionProps) {
  // Calculate the path
  const pathD = `M ${from.x} ${from.y} L ${to.x} ${to.y}`;

  // Calculate path length for animation
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const length = Math.sqrt(dx * dx + dy * dy);

  return (
    <motion.path
      d={pathD}
      className={`map-connection ${visited ? 'map-connection--visited' : 'map-connection--unvisited'}`}
      strokeDasharray={visited ? 'none' : '8 4'}
      strokeWidth={visited ? 3 : 2}
      fill="none"
      initial={{
        pathLength: 0,
        opacity: 0
      }}
      animate={{
        pathLength: 1,
        opacity: visited ? 1 : 0.4,
      }}
      transition={{
        pathLength: {
          duration: 0.5,
          delay: index * 0.02,
          ease: 'easeOut'
        },
        opacity: {
          duration: 0.3,
          delay: index * 0.02
        }
      }}
      style={{
        stroke: visited ? '#4ade80' : '#6b7280',
        strokeLinecap: 'round',
        // For path animation calculation
        strokeDashoffset: 0,
      }}
    />
  );
}

// Helper component for curved connections (optional, for more visual appeal)
export function MapConnectionCurved({ from, to, visited, index = 0 }: MapConnectionProps) {
  // Calculate control point for quadratic bezier
  const midX = (from.x + to.x) / 2;
  const midY = (from.y + to.y) / 2;

  // Add some horizontal offset to the control point for a slight curve
  const controlX = midX + (to.x - from.x) * 0.1;
  const controlY = midY;

  const pathD = `M ${from.x} ${from.y} Q ${controlX} ${controlY} ${to.x} ${to.y}`;

  return (
    <motion.path
      d={pathD}
      className={`map-connection ${visited ? 'map-connection--visited' : 'map-connection--unvisited'}`}
      strokeDasharray={visited ? 'none' : '8 4'}
      strokeWidth={visited ? 3 : 2}
      fill="none"
      initial={{
        pathLength: 0,
        opacity: 0
      }}
      animate={{
        pathLength: 1,
        opacity: visited ? 1 : 0.4,
      }}
      transition={{
        pathLength: {
          duration: 0.5,
          delay: index * 0.02,
          ease: 'easeOut'
        },
        opacity: {
          duration: 0.3,
          delay: index * 0.02
        }
      }}
      style={{
        stroke: visited ? '#4ade80' : '#6b7280',
        strokeLinecap: 'round',
      }}
    />
  );
}

export default MapConnection;
