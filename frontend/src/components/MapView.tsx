import { useEffect, useRef, useMemo } from 'react';
import { motion } from 'framer-motion';
import { MapNode } from './MapNode';
import { MapConnection } from './MapConnection';
import { useGameStore } from '../store/gameStore';
import type { GameMap, MapNode as MapNodeData } from '../types';
import '../styles/map.css';

// Layout constants
const NODE_SIZE = 60;
const NODE_SPACING_X = 100;
const NODE_SPACING_Y = 120;
const MAP_PADDING = 80;
const SVG_WIDTH = 7 * NODE_SPACING_X + MAP_PADDING * 2;

interface MapViewProps {
  map: GameMap;
  currentRow: number;
  currentCol: number | null;
}

interface NodePosition {
  node: MapNodeData;
  x: number;
  y: number;
}

interface ConnectionData {
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
  visited: boolean;
}

export function MapView({ map, currentRow, currentCol }: MapViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const moveToNode = useGameStore((state) => state.moveToNode);
  const loading = useGameStore((state) => state.loading);

  // Calculate total map height based on number of rows
  const totalRows = map.nodes.length + (map.bossNode ? 1 : 0);
  const mapHeight = totalRows * NODE_SPACING_Y + MAP_PADDING * 2;

  // Calculate node positions (inverted Y so boss is at top)
  const nodePositions = useMemo((): NodePosition[] => {
    const positions: NodePosition[] = [];

    // Add boss node at the top
    if (map.bossNode) {
      positions.push({
        node: map.bossNode,
        x: SVG_WIDTH / 2,
        y: MAP_PADDING,
      });
    }

    // Add regular nodes (inverted - higher rows appear higher on screen)
    map.nodes.forEach((row, rowIndex) => {
      const rowY = map.bossNode
        ? MAP_PADDING + (totalRows - 1 - rowIndex) * NODE_SPACING_Y
        : MAP_PADDING + (map.nodes.length - 1 - rowIndex) * NODE_SPACING_Y;

      row.forEach((node) => {
        // Calculate X position based on column, centered
        const totalCols = 7; // Assuming 7 columns max
        const startX = (SVG_WIDTH - (totalCols - 1) * NODE_SPACING_X) / 2;
        const nodeX = startX + node.col * NODE_SPACING_X;

        positions.push({
          node,
          x: nodeX,
          y: rowY,
        });
      });
    });

    return positions;
  }, [map.nodes, map.bossNode, totalRows]);

  // Calculate connections between nodes
  const connections = useMemo((): ConnectionData[] => {
    const conns: ConnectionData[] = [];
    const nodeMap = new Map<string, NodePosition>();

    // Create lookup map for node positions
    nodePositions.forEach((np) => {
      nodeMap.set(`${np.node.row}-${np.node.col}`, np);
    });

    // Generate connections
    nodePositions.forEach((np) => {
      np.node.connections.forEach((conn) => {
        const targetKey = `${conn.row}-${conn.col}`;
        const target = nodeMap.get(targetKey);

        if (target) {
          // Check if this connection was visited (both nodes visited and adjacent)
          const visited = np.node.visited && target.node.visited;

          // Only add connection once (from lower row to higher row)
          if (np.node.row < conn.row ||
              (np.node.row === conn.row && np.node.col < conn.col)) {
            conns.push({
              fromX: np.x,
              fromY: np.y,
              toX: target.x,
              toY: target.y,
              visited,
            });
          }
        }
      });
    });

    return conns;
  }, [nodePositions]);

  // Auto-scroll to current position
  useEffect(() => {
    if (containerRef.current && currentRow >= 0) {
      const currentNodePos = nodePositions.find(
        (np) => np.node.row === currentRow && np.node.col === currentCol
      );

      if (currentNodePos) {
        const container = containerRef.current;
        const scrollTarget = currentNodePos.y - container.clientHeight / 2;

        container.scrollTo({
          top: Math.max(0, scrollTarget),
          behavior: 'smooth',
        });
      }
    }
  }, [currentRow, currentCol, nodePositions]);

  const handleNodeClick = (row: number, col: number) => {
    if (!loading) {
      moveToNode(row, col);
    }
  };

  const isCurrent = (node: MapNodeData): boolean => {
    return node.row === currentRow && node.col === currentCol;
  };

  return (
    <motion.div
      className="map-view"
      ref={containerRef}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="map-view__header">
        <h2 className="map-view__title">Map</h2>
        <span className="map-view__floor">Floor {currentRow + 1}</span>
      </div>

      <div
        className="map-view__scroll-container"
        style={{ height: mapHeight }}
      >
        {/* SVG layer for connections */}
        <svg
          className="map-view__connections"
          width={SVG_WIDTH}
          height={mapHeight}
          viewBox={`0 0 ${SVG_WIDTH} ${mapHeight}`}
        >
          <defs>
            {/* Glow filter for visited paths */}
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="2" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          <g filter={undefined}>
            {connections.map((conn, index) => (
              <MapConnection
                key={`${conn.fromX}-${conn.fromY}-${conn.toX}-${conn.toY}`}
                from={{ x: conn.fromX, y: conn.fromY }}
                to={{ x: conn.toX, y: conn.toY }}
                visited={conn.visited}
                index={index}
              />
            ))}
          </g>
        </svg>

        {/* Nodes layer */}
        <div className="map-view__nodes">
          {nodePositions.map((np) => (
            <div
              key={`node-${np.node.row}-${np.node.col}`}
              className="map-view__node-wrapper"
              style={{
                left: np.x - NODE_SIZE / 2,
                top: np.y - NODE_SIZE / 2,
                width: NODE_SIZE,
                height: NODE_SIZE,
              }}
            >
              <MapNode
                node={np.node}
                isCurrent={isCurrent(np.node)}
                onClick={handleNodeClick}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="map-view__legend">
        <div className="map-view__legend-item">
          <span className="map-view__legend-icon">{'\u2694\uFE0F'}</span>
          <span>Combat</span>
        </div>
        <div className="map-view__legend-item">
          <span className="map-view__legend-icon">{'\uD83D\uDC80'}</span>
          <span>Elite</span>
        </div>
        <div className="map-view__legend-item">
          <span className="map-view__legend-icon">{'\uD83D\uDD25'}</span>
          <span>Rest</span>
        </div>
        <div className="map-view__legend-item">
          <span className="map-view__legend-icon">{'\uD83D\uDCB0'}</span>
          <span>Shop</span>
        </div>
        <div className="map-view__legend-item">
          <span className="map-view__legend-icon">{'\u2753'}</span>
          <span>Event</span>
        </div>
        <div className="map-view__legend-item">
          <span className="map-view__legend-icon">{'\uD83D\uDC8E'}</span>
          <span>Treasure</span>
        </div>
        <div className="map-view__legend-item">
          <span className="map-view__legend-icon">{'\uD83D\uDC79'}</span>
          <span>Boss</span>
        </div>
      </div>

      {loading && (
        <div className="map-view__loading">
          <motion.div
            className="map-view__loading-spinner"
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
          />
        </div>
      )}
    </motion.div>
  );
}

export default MapView;
