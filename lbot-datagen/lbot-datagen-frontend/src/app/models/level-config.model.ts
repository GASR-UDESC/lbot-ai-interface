/** Shape variant of the arena boundary. */
export type ArenaShape = 'square' | 'rectangle' | 'circle';

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
  /** Shape of the arena boundary. Defaults to 'square' when omitted. */
  arenaShape?: ArenaShape;
  /** Arena dimensions in world units. Defaults to { width: 400, height: 400 } when omitted. */
  arenaSize?: { width: number; height: number };
}

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
      // Loose diagonal cluster blocking the center. Player must skirt left or right.
      { x:   0, z:   0, width: 15, height: 15, depth: 15, type: 'crate' },
      { x: -25, z:  25, width: 15, height: 15, depth: 15, type: 'crate' },
      { x:  25, z: -25, width: 15, height: 15, depth: 15, type: 'crate' },
      { x: -60, z:  60, width: 15, height: 15, depth: 15, type: 'crate' },
      { x:  60, z: -60, width: 15, height: 15, depth: 15, type: 'crate' },
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
    startPoint: { x: -150, z: -150 },
    goalPoint:  { x: 150, z: 150 },
    obstacles: [
      // Two horizontal desk rows blocking center
      { x: -50, z:  10, width: 70, height:  8, depth: 10, type: 'wall' },
      { x:  50, z: -10, width: 70, height:  8, depth: 10, type: 'wall' },
      // Vertical walls (shelving units) on sides
      { x:   0, z: -70, width: 10, height:  8, depth: 70, type: 'wall' },
      { x:   0, z:  70, width: 10, height:  8, depth: 70, type: 'wall' },
      // Crate obstacles in corners of the main corridor
      { x: -100, z: -50, width: 15, height: 15, depth: 15, type: 'crate' },
      { x:  100, z:  50, width: 15, height: 15, depth: 15, type: 'crate' },
      // Extra wall forcing a detour on the upper route
      { x: -30, z: 100, width: 50, height: 8, depth: 10, type: 'wall' },
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
      // Tall "building" walls on left and right halves
      { x: -80, z:  15, width:  8, height: 30, depth: 130, type: 'wall' },
      { x:  80, z: -15, width:  8, height: 30, depth: 130, type: 'wall' },
      // Cross-walls blocking centre passage — leave gaps at the ends
      { x:  10, z: -55, width: 100, height: 30, depth: 8, type: 'wall' },
      { x: -10, z:  55, width: 100, height: 30, depth: 8, type: 'wall' },
      // Extra narrow alleys
      { x: -35, z: -110, width: 8, height: 30, depth: 60, type: 'wall' },
      { x:  35, z:  110, width: 8, height: 30, depth: 60, type: 'wall' },
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
    startPoint: { x: -150, z: -150 },
    goalPoint:  { x: 150, z: 150 },
    obstacles: [
      // "Trees" — tall narrow crates arranged in a sinuous pattern
      { x:  -90, z:  -50, width: 12, height: 25, depth: 12, type: 'crate' },
      { x:  -40, z: -100, width: 12, height: 25, depth: 12, type: 'crate' },
      { x:   15, z:  -55, width: 12, height: 25, depth: 12, type: 'crate' },
      { x:  -70, z:   25, width: 12, height: 25, depth: 12, type: 'crate' },
      { x:  -20, z:   55, width: 12, height: 25, depth: 12, type: 'crate' },
      { x:   45, z:   10, width: 12, height: 25, depth: 12, type: 'crate' },
      { x:   85, z:  -35, width: 12, height: 25, depth: 12, type: 'crate' },
      { x:   25, z:  100, width: 12, height: 25, depth: 12, type: 'crate' },
      { x:  100, z:   70, width: 12, height: 25, depth: 12, type: 'crate' },
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
    startPoint: { x: -150, z: -150 },
    goalPoint:  { x: 150, z: 150 },
    obstacles: [
      // Long industrial walls forming a partial maze
      { x: -60, z:  -45, width:  8, height: 18, depth:  90, type: 'wall' },
      { x:  60, z:   45, width:  8, height: 18, depth:  90, type: 'wall' },
      { x:   0, z:    0, width: 90, height: 18, depth:   8, type: 'wall' },
      // Crate obstacles blocking secondary routes
      { x: -100, z:  35, width: 15, height: 15, depth: 15, type: 'crate' },
      { x:  100, z: -35, width: 15, height: 15, depth: 15, type: 'crate' },
      { x:   35, z: -100, width: 15, height: 15, depth: 15, type: 'crate' },
      { x:  -35, z:  100, width: 15, height: 15, depth: 15, type: 'crate' },
      // Ramps — industrial conveyor belt aesthetic
      { x:  -50, z:  70, width: 40, height: 3, depth: 50, type: 'ramp', rampAngle: 0.3927 },
      { x:   50, z: -70, width: 40, height: 3, depth: 50, type: 'ramp', rampAngle: 0.3927 },
    ]
  },
];
