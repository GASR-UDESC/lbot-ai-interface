/**
 * Visual theme configuration for a game level.
 */
export interface ThemeConfig {
  /** Ground/floor color (hex string, e.g. '#8B4513') */
  groundColor: string;
  /** Arena boundary wall color */
  wallColor: string;
  /** Obstacle color */
  obstacleColor: string;
  /** Sky/background color */
  skyColor: string;
}

/** Geometry/behavior type of an obstacle */
export type ObstacleType = 'wall' | 'crate' | 'ramp';

/**
 * Configuration for a single obstacle within a level.
 */
export interface ObstacleConfig {
  /** X position in the arena */
  x: number;
  /** Z position in the arena */
  z: number;
  /** Width of the obstacle (X axis) */
  width: number;
  /** Height of the obstacle (Y axis) */
  height: number;
  /** Depth of the obstacle (Z axis) */
  depth: number;
  /** Obstacle type affecting rendering and physics */
  type: ObstacleType;
  /** Optional Y rotation in degrees */
  rotationY?: number;
  /** Optional X-axis tilt angle in radians (used for ramps) */
  rampAngle?: number;
}

/**
 * Full configuration for a game level, including theme, obstacles and fixed start/goal points.
 */
export interface LevelConfig {
  /** Unique level identifier (1-5) */
  id: number;
  /** Display name of the level */
  name: string;
  /** Visual theme applied to ground, walls and obstacles */
  theme: ThemeConfig;
  /** List of obstacles in this level */
  obstacles: ObstacleConfig[];
  /** Robot starting position */
  startPoint: { x: number; z: number };
  /** Goal (point B) position */
  goalPoint: { x: number; z: number };
}

const PLAYABLE_EDGE = 185;

function createHorizontalGapWalls(
  z: number,
  gapCenter: number,
  gapWidth: number,
  height = 18,
  depth = 12
): ObstacleConfig[] {
  const gapStart = gapCenter - gapWidth / 2;
  const gapEnd = gapCenter + gapWidth / 2;
  const walls: ObstacleConfig[] = [];

  if (gapStart > -PLAYABLE_EDGE) {
    walls.push({
      x: (-PLAYABLE_EDGE + gapStart) / 2,
      z,
      width: gapStart + PLAYABLE_EDGE,
      height,
      depth,
      type: 'wall'
    });
  }

  if (gapEnd < PLAYABLE_EDGE) {
    walls.push({
      x: (gapEnd + PLAYABLE_EDGE) / 2,
      z,
      width: PLAYABLE_EDGE - gapEnd,
      height,
      depth,
      type: 'wall'
    });
  }

  return walls;
}

function createVerticalGapWalls(
  x: number,
  gapCenter: number,
  gapWidth: number,
  height = 18,
  width = 12
): ObstacleConfig[] {
  const gapStart = gapCenter - gapWidth / 2;
  const gapEnd = gapCenter + gapWidth / 2;
  const walls: ObstacleConfig[] = [];

  if (gapStart > -PLAYABLE_EDGE) {
    walls.push({
      x,
      z: (-PLAYABLE_EDGE + gapStart) / 2,
      width,
      height,
      depth: gapStart + PLAYABLE_EDGE,
      type: 'wall'
    });
  }

  if (gapEnd < PLAYABLE_EDGE) {
    walls.push({
      x,
      z: (gapEnd + PLAYABLE_EDGE) / 2,
      width,
      height,
      depth: PLAYABLE_EDGE - gapEnd,
      type: 'wall'
    });
  }

  return walls;
}

/**
 * Definitions for all 5 game levels.
 *
 * Level design philosophy:
 *  - Level 1-2: horizontal barriers with alternating gaps forcing S-shaped detours.
 *  - Level 3: corridor route with narrow transitions and mandatory turns.
 *  - Level 4: denser maze with longer route options and more decision points.
 *  - Level 5: industrial maze that funnels the robot into a ramp-only final passage.
 */
export const LEVEL_CONFIGS: LevelConfig[] = [
  // ─────────────────────────────────────────────
  // Level 1 — Armazem (Warehouse)
  // ─────────────────────────────────────────────
  {
    id: 1,
    name: 'Armazém',
    theme: {
      groundColor: '#8B4513',
      wallColor:   '#A0522D',
      obstacleColor: '#D2691E',
      skyColor:    '#87CEEB'
    },
    startPoint: { x: -150, z: -150 },
    goalPoint:  { x: 150, z: 150 },
    obstacles: [
      ...createHorizontalGapWalls(-85, -135, 60, 16, 12),
      ...createHorizontalGapWalls(10, 125, 60, 16, 12),
      ...createHorizontalGapWalls(105, -25, 70, 16, 12),
    ]
  },

  // ─────────────────────────────────────────────
  // Level 2 — Escritorio (Office)
  // ─────────────────────────────────────────────
  {
    id: 2,
    name: 'Escritório',
    theme: {
      groundColor: '#C0C0C0',
      wallColor:   '#808080',
      obstacleColor: '#A0A0A0',
      skyColor:    '#B0C4DE'
    },
    startPoint: { x: -155, z: -155 },
    goalPoint:  { x: 155, z: 145 },
    obstacles: [
      ...createHorizontalGapWalls(-110, 130, 55, 18, 12),
      { x: 92, z: -82, width: 18, height: 18, depth: 18, type: 'crate' },
      ...createHorizontalGapWalls(-35, -120, 55, 18, 12),
      { x: -75, z: -8, width: 18, height: 18, depth: 18, type: 'crate' },
      ...createHorizontalGapWalls(40, 0, 60, 18, 12),
      ...createHorizontalGapWalls(120, 135, 55, 18, 12),
    ]
  },

  // ─────────────────────────────────────────────
  // Level 3 — Cidade (City)
  // ─────────────────────────────────────────────
  {
    id: 3,
    name: 'Cidade',
    theme: {
      groundColor: '#4A4A4A',
      wallColor:   '#333333',
      obstacleColor: '#555555',
      skyColor:    '#708090'
    },
    startPoint: { x: -150, z: -150 },
    goalPoint:  { x: 150, z: 150 },
    obstacles: [
      ...createVerticalGapWalls(-65, -145, 45, 22, 12),
      ...createHorizontalGapWalls(-60, -10, 45, 22, 12),
      ...createVerticalGapWalls(35, -10, 45, 22, 12),
      ...createHorizontalGapWalls(70, 115, 45, 22, 12),
      ...createVerticalGapWalls(125, 115, 45, 22, 12),
    ]
  },

  // ─────────────────────────────────────────────
  // Level 4 — Floresta (Forest)
  // ─────────────────────────────────────────────
  {
    id: 4,
    name: 'Floresta',
    theme: {
      groundColor: '#228B22',
      wallColor:   '#8B4513',
      obstacleColor: '#006400',
      skyColor:    '#87CEEB'
    },
    startPoint: { x: -170, z: -170 },
    goalPoint:  { x: 170, z: 170 },
    obstacles: [
      ...createVerticalGapWalls(-125, -150, 45, 24, 12),
      ...createHorizontalGapWalls(-120, -55, 45, 24, 12),
      ...createVerticalGapWalls(-35, -30, 45, 24, 12),
      ...createHorizontalGapWalls(-25, 120, 50, 24, 12),
      ...createVerticalGapWalls(55, 95, 45, 24, 12),
      ...createHorizontalGapWalls(65, 110, 50, 24, 12),
      ...createVerticalGapWalls(145, 145, 45, 24, 12),
      { x: -85, z: 20, width: 90, height: 24, depth: 12, type: 'wall' },
      { x: 105, z: -85, width: 12, height: 24, depth: 100, type: 'wall' },
      { x: 25, z: 125, width: 90, height: 24, depth: 12, type: 'wall' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 5 — Fabrica (Factory)
  // ─────────────────────────────────────────────
  {
    id: 5,
    name: 'Fábrica',
    theme: {
      groundColor: '#2F4F4F',
      wallColor:   '#1C1C1C',
      obstacleColor: '#3D3D3D',
      skyColor:    '#404040'
    },
    startPoint: { x: -170, z: -170 },
    goalPoint:  { x: 160, z: 160 },
    obstacles: [
      ...createHorizontalGapWalls(-115, -130, 50, 24, 12),
      ...createVerticalGapWalls(-70, -45, 45, 24, 12),
      ...createHorizontalGapWalls(-20, 120, 50, 24, 12),
      { x: 78, z: 60, width: 12, height: 24, depth: 180, type: 'wall' },
      { x: 162, z: 60, width: 12, height: 24, depth: 180, type: 'wall' },
      { x: 120, z: 60, width: 72, height: 20, depth: 14, type: 'wall' },
      { x: 120, z: 22, width: 34, height: 6, depth: 54, type: 'ramp', rampAngle: 0.42 },
      { x: 120, z: 98, width: 34, height: 6, depth: 54, type: 'ramp', rotationY: 180, rampAngle: 0.42 },
      ...createHorizontalGapWalls(135, 120, 50, 24, 12),
    ]
  },
];
