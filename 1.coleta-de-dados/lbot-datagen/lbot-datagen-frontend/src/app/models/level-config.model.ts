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
export type ObstacleType = 'wall' | 'crate' | 'ramp' | 'tree' | 'barrier' | 'stack' | 'industrial';

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

// ---------------------------------------------------------------------------
// Fixed start and goal points used across ALL levels.
// A = (-150, -150) | B = (150, 150) | distance ≈ 424 units
// ---------------------------------------------------------------------------
const START_POINT = { x: -150, z: -150 };
const GOAL_POINT = { x: 150, z: 150 };

/**
 * Definitions for all 5 game levels.
 *
 * Level design philosophy:
 *  - Nivel 1 (Trivial)  : few crates, almost straight path. Tutorial intro.
 *  - Nivel 2 (Desviar)  : walls creating detours, no ramps. Corner blocking.
 *  - Nivel 3 (Labirinto): first mandatory ramp, corners blocked, U-shaped walls.
 *  - Nivel 4 (Denso)   : dense labyrinth with narrow corridors, one mandatory ramp.
 *  - Nivel 5 (Complexo) : two mandatory ramps, mixed obstacles, most complex layout.
 */
export const LEVEL_CONFIGS: LevelConfig[] = [
  // ─────────────────────────────────────────────
  // Level 1 — Nivel 1
  // ─────────────────────────────────────────────
  {
    id: 1,
    name: 'Nivel 1',
    theme: {
      groundColor: '#7C9A5E',
      wallColor:   '#8B7355',
      obstacleColor: '#A67B5B',
      skyColor:    '#87CEEB'
    },
    startPoint: START_POINT,
    goalPoint:  GOAL_POINT,
    obstacles: [
      // Tutorial level — sparse crates near centre, easy to go around
      { x:   0, z:   0, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: -25, z:  25, width: 10, height: 10, depth: 10, type: 'crate' },
      { x:  25, z: -25, width: 10, height: 10, depth: 10, type: 'crate' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 2 — Nivel 2
  // ─────────────────────────────────────────────
  {
    id: 2,
    name: 'Nivel 2',
    theme: {
      groundColor: '#D3D3D3',
      wallColor:   '#808080',
      obstacleColor: '#A9A9A9',
      skyColor:    '#B0C4DE'
    },
    startPoint: START_POINT,
    goalPoint:  GOAL_POINT,
    obstacles: [
      // Central vertical wall — blocks the direct diagonal A→B
      { x:   0, z:   0, width: 10, height: 18, depth: 120, type: 'wall' },
      // Horizontal walls that force zig-zag detours
      { x: -80, z:   0, width: 60, height: 15, depth: 10, type: 'wall' },
      { x:  80, z:   0, width: 60, height: 15, depth: 10, type: 'wall' },
      // Vertical barriers channelling into narrow corridors
      { x:   0, z:  90, width: 10, height: 15, depth: 60, type: 'wall' },
      { x:   0, z: -90, width: 10, height: 15, depth: 60, type: 'wall' },
      // Corner blocking — NE / SW arena corners
      { x:  130, z:  60, width: 10, height: 15, depth: 80, type: 'wall' },
      { x:  60, z:  130, width: 80, height: 15, depth: 10, type: 'wall' },
      { x: -130, z: -60, width: 10, height: 15, depth: 80, type: 'wall' },
      { x:  -60, z: -130, width: 80, height: 15, depth: 10, type: 'wall' },
      // Extra walls to reinforce detour path
      { x: -50, z:  50, width: 40, height: 12, depth: 10, type: 'wall' },
      { x:  50, z: -50, width: 40, height: 12, depth: 10, type: 'wall' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 3 — Nivel 3
  // ─────────────────────────────────────────────
  {
    id: 3,
    name: 'Nivel 3',
    theme: {
      groundColor: '#696969',
      wallColor:   '#2F4F4F',
      obstacleColor: '#708090',
      skyColor:    '#778899'
    },
    startPoint: START_POINT,
    goalPoint:  GOAL_POINT,
    obstacles: [
      // Mandatory ramp — the only passage through the centre barrier
      { x:   0, z:   0, width: 36, height: 3, depth: 60, type: 'ramp', rotationY: 45, rampAngle: 0.24 },
      // Long centre walls flanking the ramp (forming a narrow corridor)
      { x: -30, z:   0, width: 8, height: 18, depth: 180, type: 'wall' },
      { x:  30, z:   0, width: 8, height: 18, depth: 180, type: 'wall' },
      // Horizontal barriers extending from corridor walls to arena edges
      { x: -90, z: 100, width: 120, height: 15, depth: 8, type: 'wall' },
      { x:  90, z: -100, width: 120, height: 15, depth: 8, type: 'wall' },
      // Corner blocking — all four corners
      { x: -130, z: -70, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:  -70, z: -130, width: 60, height: 15, depth: 8, type: 'wall' },
      { x: -130, z:  70, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:  -70, z:  130, width: 60, height: 15, depth: 8, type: 'wall' },
      { x:  130, z: -70, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:   70, z: -130, width: 60, height: 15, depth: 8, type: 'wall' },
      { x:  130, z:  70, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:   70, z:  130, width: 60, height: 15, depth: 8, type: 'wall' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 4 — Nivel 4
  // ─────────────────────────────────────────────
  {
    id: 4,
    name: 'Nivel 4',
    theme: {
      groundColor: '#228B22',
      wallColor:   '#8B4513',
      obstacleColor: '#006400',
      skyColor:    '#98FB98'
    },
    startPoint: START_POINT,
    goalPoint:  GOAL_POINT,
    obstacles: [
      // Mandatory ramp at centre
      { x:   0, z:   0, width: 30, height: 3, depth: 50, type: 'ramp', rotationY: 45, rampAngle: 0.24 },
      // Corridor walls flanking the ramp
      { x: -30, z:   0, width: 8, height: 18, depth: 140, type: 'wall' },
      { x:  30, z:   0, width: 8, height: 18, depth: 140, type: 'wall' },
      // Walls to funnel into the corridor
      { x: -70, z: -60, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:  70, z:  60, width: 8, height: 15, depth: 60, type: 'wall' },
      // Trees acting as extra obstacles near the path
      { x:  -80, z:  -80, width: 18, height: 20, depth: 18, type: 'tree' },
      { x:   80, z:   80, width: 18, height: 20, depth: 18, type: 'tree' },
      // Barrier walls near the corridor entrances
      { x:  -90, z:  100, width: 40, height: 15, depth: 8, type: 'barrier' },
      { x:   90, z: -100, width: 40, height: 15, depth: 8, type: 'barrier' },
      // Corner blocking — all four corners
      { x: -130, z: -70, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:  -70, z: -130, width: 60, height: 15, depth: 8, type: 'wall' },
      { x: -130, z:  70, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:  -70, z:  130, width: 60, height: 15, depth: 8, type: 'wall' },
      { x:  130, z: -70, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:   70, z: -130, width: 60, height: 15, depth: 8, type: 'wall' },
      { x:  130, z:  70, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:   70, z:  130, width: 60, height: 15, depth: 8, type: 'wall' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 5 — Nivel 5
  // ─────────────────────────────────────────────
  {
    id: 5,
    name: 'Nivel 5',
    theme: {
      groundColor: '#2F4F4F',
      wallColor:   '#1C1C1C',
      obstacleColor: '#FF6600',
      skyColor:    '#404040'
    },
    startPoint: START_POINT,
    goalPoint:  GOAL_POINT,
    obstacles: [
      // First mandatory ramp (lower section, near A side)
      { x: -30, z: -30, width: 28, height: 3, depth: 45, type: 'ramp', rotationY: 45, rampAngle: 0.24 },
      // Second mandatory ramp (upper section, near B side)
      { x:  60, z:  60, width: 28, height: 3, depth: 45, type: 'ramp', rotationY: 45, rampAngle: 0.24 },
      // Walls flanking first ramp
      { x: -55, z:  -8, width: 8, height: 15, depth: 80, type: 'wall' },
      { x:  -8, z: -55, width: 8, height: 15, depth: 80, type: 'wall' },
      // Walls flanking second ramp
      { x:  35, z:  80, width: 8, height: 15, depth: 80, type: 'wall' },
      { x:  80, z:  35, width: 8, height: 15, depth: 80, type: 'wall' },
      // Additional corridor walls to force detours
      { x: -100, z:  30, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:  100, z: -30, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:   30, z: -100, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:  -30, z:  100, width: 8, height: 15, depth: 60, type: 'wall' },
      // Mixed obstacles — industrial structures
      { x:  -80, z:   80, width: 22, height: 18, depth: 22, type: 'industrial' },
      { x:   80, z:  -80, width: 22, height: 18, depth: 22, type: 'industrial' },
      // Crate stacks
      { x: -120, z: -120, width: 14, height: 14, depth: 14, type: 'stack' },
      { x:  120, z:  120, width: 14, height: 14, depth: 14, type: 'stack' },
      // Trees
      { x:  -60, z:  120, width: 18, height: 20, depth: 18, type: 'tree' },
      { x:   60, z: -120, width: 18, height: 20, depth: 18, type: 'tree' },
      // Corner blocking
      { x: -130, z: -70, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:  -70, z: -130, width: 60, height: 15, depth: 8, type: 'wall' },
      { x: -130, z:  70, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:  -70, z:  130, width: 60, height: 15, depth: 8, type: 'wall' },
      { x:  130, z:  70, width: 8, height: 15, depth: 60, type: 'wall' },
      { x:   70, z:  130, width: 60, height: 15, depth: 8, type: 'wall' },
    ]
  },
];
