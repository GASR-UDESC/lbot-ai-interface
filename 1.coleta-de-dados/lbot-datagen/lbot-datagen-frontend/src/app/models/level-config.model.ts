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
 *  - Level 1 (Armazem)  : 5 crates in a loose diagonal cluster. Easy to go around.
 *  - Level 2 (Escritorio): 7 rectangular obstacles (desks/shelves). More blocked paths.
 *  - Level 3 (Cidade)   : 6 tall walls creating narrow corridors and forced detours.
 *  - Level 4 (Floresta) : 9 tall "tree" crates placed in a sinuous pattern.
 *  - Level 5 (Fabrica)  : 9 mixed obstacles (walls + crates + ramps). Most complex.
 */
export const LEVEL_CONFIGS: LevelConfig[] = [
  // ─────────────────────────────────────────────
  // Level 1 — Campo de Treino (Training Ground)
  // ─────────────────────────────────────────────
  {
    id: 1,
    name: 'Campo de Treino',
    theme: {
      groundColor: '#7C9A5E',
      wallColor:   '#8B7355',
      obstacleColor: '#A67B5B',
      skyColor:    '#87CEEB'
    },
    startPoint: START_POINT,
    goalPoint:  GOAL_POINT,
    obstacles: [
      // Loose diagonal cluster in the centre; small detours left/right keep path almost straight.
      { x:   0, z:   0, width: 15, height: 15, depth: 15, type: 'crate' },
      { x: -20, z:  20, width: 12, height: 12, depth: 12, type: 'crate' },
      { x:  20, z: -20, width: 12, height: 12, depth: 12, type: 'crate' },
      { x:   0, z:  40, width: 10, height: 10, depth: 10, type: 'crate' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 2 — Escritorio Central (Central Office)
  // ─────────────────────────────────────────────
  {
    id: 2,
    name: 'Escritório Central',
    theme: {
      groundColor: '#D3D3D3',
      wallColor:   '#808080',
      obstacleColor: '#A9A9A9',
      skyColor:    '#B0C4DE'
    },
    startPoint: START_POINT,
    goalPoint:  GOAL_POINT,
    obstacles: [
      // Central vertical partition — forces detour around it
      { x:   0, z:   0, width: 10, height: 15, depth: 80, type: 'wall' },
      // Horizontal walls on left/right that block the straight corridor
      { x: -80, z:   0, width: 60, height: 12, depth: 10, type: 'wall' },
      { x:  80, z:   0, width: 60, height: 12, depth: 10, type: 'wall' },
      // Upper/lower vertical walls channelling the player into a corridor
      { x:   0, z:  80, width: 10, height: 12, depth: 60, type: 'wall' },
      { x:   0, z: -80, width: 10, height: 12, depth: 60, type: 'wall' },
      // Extra corner walls forcing additional turns
      { x: -40, z:  40, width: 40, height: 10, depth: 10, type: 'wall' },
      { x:  40, z: -40, width: 40, height: 10, depth: 10, type: 'wall' },
      // Block L-shaped paths along the bottom and left edges (leave gap at center)
      { x: -60, z: -130, width: 80, height: 12, depth: 10, type: 'wall' },
      { x:  60, z: -130, width: 80, height: 12, depth: 10, type: 'wall' },
      { x: -130, z: -60, width: 10, height: 12, depth: 80, type: 'wall' },
      { x: -130, z:  60, width: 10, height: 12, depth: 80, type: 'wall' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 3 — Cidade em Obras (City Under Construction)
  // ─────────────────────────────────────────────
  {
    id: 3,
    name: 'Cidade em Obras',
    theme: {
      groundColor: '#696969',
      wallColor:   '#2F4F4F',
      obstacleColor: '#708090',
      skyColor:    '#778899'
    },
    startPoint: START_POINT,
    goalPoint:  GOAL_POINT,
    obstacles: [
      // Main ramp aligned with the NE diagonal path (45°) so the robot can climb it
      { x:   0, z:   0, width: 40, height: 3, depth: 50, type: 'ramp', rotationY: 45, rampAngle: 0.3927 },
      // Side barriers funnelling the robot toward the ramp
      { x: -50, z:  50, width: 15, height: 10, depth: 5, type: 'barrier' },
      { x:  50, z: -50, width: 15, height: 10, depth: 5, type: 'barrier' },
      { x: -80, z:  20, width: 15, height: 10, depth: 5, type: 'barrier' },
      { x:  80, z: -20, width: 15, height: 10, depth: 5, type: 'barrier' },
      // Large diagonal walls blocking the outer edges
      { x: -80, z:  80, width: 10, height: 15, depth: 80, type: 'wall' },
      { x:  80, z: -80, width: 10, height: 15, depth: 80, type: 'wall' },
      // Horizontal walls blocking top/bottom routes
      { x:   0, z: 100, width: 80, height: 12, depth: 10, type: 'wall' },
      { x:   0, z: -100, width: 80, height: 12, depth: 10, type: 'wall' },
      // Additional barriers near the start/goal to prevent easy bypasses
      { x: -100, z:   0, width: 20, height: 8, depth: 5, type: 'barrier' },
      { x:  100, z:   0, width: 20, height: 8, depth: 5, type: 'barrier' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 4 — Floresta Misteriosa (Mysterious Forest)
  // ─────────────────────────────────────────────
  {
    id: 4,
    name: 'Floresta Misteriosa',
    theme: {
      groundColor: '#228B22',
      wallColor:   '#8B4513',
      obstacleColor: '#006400',
      skyColor:    '#98FB98'
    },
    startPoint: START_POINT,
    goalPoint:  GOAL_POINT,
    obstacles: [
      // Trees (trunk + canopy) with varied angles to force zig-zag
      { x:  -80, z:  -80, width: 18, height: 20, depth: 18, type: 'tree', rotationY: 45 },
      { x:  -30, z:  -30, width: 18, height: 20, depth: 18, type: 'tree', rotationY: 15 },
      { x:   20, z:   20, width: 18, height: 20, depth: 18, type: 'tree', rotationY: 30 },
      { x:   70, z:   70, width: 18, height: 20, depth: 18, type: 'tree', rotationY: 60 },
      { x:  100, z:  100, width: 18, height: 20, depth: 18, type: 'tree', rotationY: 75 },
      { x:   40, z:  -40, width: 18, height: 20, depth: 18, type: 'tree', rotationY: 30 },
      // Barriers at angles to create additional detours
      { x: -120, z:   30, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 45 },
      { x:   30, z:  120, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 30 },
      { x:  120, z:  -30, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 60 },
      { x:  -30, z: -120, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 45 },
      { x:  -60, z:   80, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 15 },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 5 — Complexo Industrial (Industrial Complex)
  // ─────────────────────────────────────────────
  {
    id: 5,
    name: 'Complexo Industrial',
    theme: {
      groundColor: '#2F4F4F',
      wallColor:   '#1C1C1C',
      obstacleColor: '#FF6600',
      skyColor:    '#404040'
    },
    startPoint: START_POINT,
    goalPoint:  GOAL_POINT,
    obstacles: [
      // Central corridor walls — create narrow passages
      { x:  -50, z:  -50, width: 10, height: 18, depth: 100, type: 'wall' },
      { x:   50, z:   50, width: 10, height: 18, depth: 100, type: 'wall' },
      // Full-width horizontal walls blocking top/bottom edges
      { x:    0, z: -120, width: 200, height: 18, depth: 10, type: 'wall' },
      { x:    0, z:  120, width: 200, height: 18, depth: 10, type: 'wall' },
      // Full-depth vertical walls blocking left/right edges
      { x: -120, z:    0, width: 10, height: 18, depth: 200, type: 'wall' },
      { x:  120, z:    0, width: 10, height: 18, depth: 200, type: 'wall' },
      // Central ramp aligned with diagonal path (45°)
      { x:    0, z:    0, width: 30, height: 3, depth: 60, type: 'ramp', rampAngle: 0.3927, rotationY: 45 },
      // Industrial complex structures
      { x:  -60, z:   40, width: 30, height: 20, depth: 30, type: 'industrial' },
      { x:   60, z:  -40, width: 30, height: 20, depth: 30, type: 'industrial' },
      { x:  -20, z:  -80, width: 30, height: 20, depth: 30, type: 'industrial' },
      { x:   20, z:   80, width: 30, height: 20, depth: 30, type: 'industrial' },
      // Crate stacks
      { x:   40, z:  -40, width: 15, height: 15, depth: 15, type: 'stack' },
      { x:  -40, z:   40, width: 15, height: 15, depth: 15, type: 'stack' },
      { x: -120, z:  120, width: 15, height: 15, depth: 15, type: 'stack' },
      { x:  120, z: -120, width: 15, height: 15, depth: 15, type: 'stack' },
      { x:   80, z:   80, width: 15, height: 15, depth: 15, type: 'stack' },
      { x:  -80, z:  -80, width: 15, height: 15, depth: 15, type: 'stack' },
      // Rotated barriers at angles creating zig-zag
      { x:   70, z:   70, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 45 },
      { x:  -70, z:  -70, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 45 },
      { x:   30, z:  -70, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 30 },
      { x:  -30, z:   70, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 60 },
      { x:    0, z:   60, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 15 },
      { x:    0, z:  -60, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 75 },
      { x:   60, z:    0, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 30 },
      { x:  -60, z:    0, width: 20, height: 10, depth: 5, type: 'barrier', rotationY: 60 },
      // Additional walls to force more detours
      { x:  -30, z:  -30, width: 10, height: 18, depth: 60, type: 'wall' },
      { x:   30, z:   30, width: 10, height: 18, depth: 60, type: 'wall' },
      { x:  -90, z:   90, width: 10, height: 18, depth: 40, type: 'wall' },
      { x:   90, z:  -90, width: 10, height: 18, depth: 40, type: 'wall' },
    ]
  },
];
