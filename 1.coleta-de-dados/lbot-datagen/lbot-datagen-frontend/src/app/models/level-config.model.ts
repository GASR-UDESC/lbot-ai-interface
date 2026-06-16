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
// Wall helpers
// ---------------------------------------------------------------------------
function wall(x: number, z: number, w: number, d: number, h = 18): ObstacleConfig {
  return { x, z, width: w, height: h, depth: d, type: 'wall' };
}

// ---------------------------------------------------------------------------
// Corner blocker helpers (L-shaped walls near arena borders)
// ---------------------------------------------------------------------------
function cornerBlockerNE(): ObstacleConfig[] {
  return [
    wall(130, 60, 6, 80, 15),
    wall(60, 130, 80, 6, 15),
  ];
}
function cornerBlockerNW(): ObstacleConfig[] {
  return [
    wall(-130, 60, 6, 80, 15),
    wall(-60, 130, 80, 6, 15),
  ];
}
function cornerBlockerSE(): ObstacleConfig[] {
  return [
    wall(130, -60, 6, 80, 15),
    wall(60, -130, 80, 6, 15),
  ];
}
function cornerBlockerSW(): ObstacleConfig[] {
  return [
    wall(-130, -60, 6, 80, 15),
    wall(-60, -130, 80, 6, 15),
  ];
}

// ---------------------------------------------------------------------------
// Maze grid: 3×3 cells, each 100×100 units, separated by 6-unit thick walls
// Grid lines at x = -50, 50 and z = -50, 50
// ---------------------------------------------------------------------------

/** Vertical grid wall at x, with gap from zStart to zEnd (relative to x line) */
function vGrid(x: number, zStart: number, zEnd: number): ObstacleConfig[] {
  const walls: ObstacleConfig[] = [];
  if (zStart > -150) {
    walls.push(wall(x, (zStart + -150) / 2, 6, zStart - -150));
  }
  if (zEnd < 150) {
    walls.push(wall(x, (zEnd + 150) / 2, 6, 150 - zEnd));
  }
  return walls;
}

/** Horizontal grid wall at z, with gap from xStart to xEnd (relative to z line) */
function hGrid(z: number, xStart: number, xEnd: number): ObstacleConfig[] {
  const walls: ObstacleConfig[] = [];
  if (xStart > -150) {
    walls.push(wall((xStart + -150) / 2, z, xStart - -150, 6));
  }
  if (xEnd < 150) {
    walls.push(wall((xEnd + 150) / 2, z, 150 - xEnd, 6));
  }
  return walls;
}

/**
 * Definitions for all 5 game levels.
 *
 * Maze grid: 3×3 cells of 100×100 each. Walls at x=-50,50 and z=-50,50.
 * Gaps in walls create guaranteed paths between cells.
 */
export const LEVEL_CONFIGS: LevelConfig[] = [
  // ═══════════════════════════════════════════════════════════════════════
  // Level 1 — Nivel 1 (Tutorial)
  // Start: (-100,-100)  Goal: (100,100)
  // ═══════════════════════════════════════════════════════════════════════
  {
    id: 1,
    name: 'Nivel 1',
    theme: {
      groundColor: '#7C9A5E',
      wallColor: '#8B7355',
      obstacleColor: '#A67B5B',
      skyColor: '#87CEEB'
    },
    startPoint: { x: -100, z: -100 },
    goalPoint: { x: 100, z: 100 },
    obstacles: [
      // One central wall — easy to go around
      wall(0, 0, 6, 120, 18),
      // Some crates
      { x: -40, z: 40, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: 40, z: -40, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: 0, z: 80, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: 0, z: -80, width: 12, height: 12, depth: 12, type: 'crate' },
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════
  // Level 2 — Nivel 2 (Entrar)
  // Start: (-100,-100)  Goal: (0,0)
  // ═══════════════════════════════════════════════════════════════════════
  {
    id: 2,
    name: 'Nivel 2',
    theme: {
      groundColor: '#D3D3D3',
      wallColor: '#808080',
      obstacleColor: '#A9A9A9',
      skyColor: '#B0C4DE'
    },
    startPoint: { x: -100, z: -100 },
    goalPoint: { x: 0, z: 0 },
    obstacles: [
      // Corner blockers (confine start corner)
      wall(-150, -90, 6, 60, 15),
      wall(-90, -150, 60, 6, 15),

      // Grid wall at x=-50: gap from z=-50 to z=50 (connects SO↔S, blocks SO↔O)
      ...vGrid(-50, -50, 50),

      // Grid wall at z=-50: gap from x=-50 to x=50 (connects S↔Centre, blocks SO↔S)
      ...hGrid(-50, -50, 50),

      // Grid wall at x=50: gap from z=-50 to z=50 (connects Centre↔E, blocks Centre↔N)
      ...vGrid(50, -50, 50),

      // Grid wall at z=50: gap from x=-50 to x=50 (connects Centre↔N, blocks E↔NE)
      ...hGrid(50, -50, 50),

      // Goal corner blocker
      wall(0, 50, 40, 6, 15),
      wall(50, 0, 6, 40, 15),
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════
  // Level 3 — Nivel 3 (Sair)
  // Start: (0,0)  Goal: (100,100)
  // ═══════════════════════════════════════════════════════════════════════
  {
    id: 3,
    name: 'Nivel 3',
    theme: {
      groundColor: '#696969',
      wallColor: '#2F4F4F',
      obstacleColor: '#708090',
      skyColor: '#778899'
    },
    startPoint: { x: 0, z: 0 },
    goalPoint: { x: 100, z: 100 },
    obstacles: [
      // Corner blockers (confine start area)
      wall(-50, 0, 6, 60, 15),
      wall(0, -50, 60, 6, 15),

      // Grid wall at x=-50: gap from z=-50 to z=50 (connects Centre↔O, blocks Centre↔SO)
      ...vGrid(-50, -50, 50),

      // Grid wall at z=-50: gap from x=-50 to x=50 (connects Centre↔S, blocks SO↔S)
      ...hGrid(-50, -50, 50),

      // Grid wall at x=50: gap from z=-50 to z=50 (connects Centre↔E, blocks Centre↔NE)
      ...vGrid(50, -50, 50),

      // Grid wall at z=50: gap from x=-50 to x=50 (connects Centre↔N, blocks E↔NE)
      ...hGrid(50, -50, 50),

      // Goal corner blockers
      wall(150, 90, 6, 60, 15),
      wall(90, 150, 60, 6, 15),
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════
  // Level 4 — Nivel 4 (Atravessar)
  // Start: (-100,100)  Goal: (100,-100)
  // All 4 corners blocked. No border access.
  // ═══════════════════════════════════════════════════════════════════════
  {
    id: 4,
    name: 'Nivel 4',
    theme: {
      groundColor: '#228B22',
      wallColor: '#8B4513',
      obstacleColor: '#006400',
      skyColor: '#98FB98'
    },
    startPoint: { x: -100, z: 100 },
    goalPoint: { x: 100, z: -100 },
    obstacles: [
      // All 4 corner blockers
      ...cornerBlockerNW(),
      ...cornerBlockerNE(),
      ...cornerBlockerSE(),
      ...cornerBlockerSW(),

      // Grid wall at x=-50: gap from z=-50 to z=50 (connects NO↔N, O↔Centre, SO↔S)
      ...vGrid(-50, -50, 50),

      // Grid wall at z=-50: gap from x=-50 to x=50 (connects S↔Centre, SO↔S)
      ...hGrid(-50, -50, 50),

      // Grid wall at x=50: gap from z=-50 to z=50 (connects Centre↔E, NE↔N)
      ...vGrid(50, -50, 50),

      // Grid wall at z=50: gap from x=-50 to x=50 (connects N↔Centre, NE↔N)
      ...hGrid(50, -50, 50),
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════
  // Level 5 — Nivel 5 (Complexo)
  // Start: (100,-100)  Goal: (-100,100)
  // Hashtag maze pattern with dead-ends, crates, ramps and industrial stacks
  // ═══════════════════════════════════════════════════════════════════════
  {
    id: 5,
    name: 'Nivel 5',
    theme: {
      groundColor: '#2F4F4F',
      wallColor: '#1C1C1C',
      obstacleColor: '#FF6600',
      skyColor: '#404040'
    },
    startPoint: { x: 100, z: -100 },
    goalPoint: { x: -100, z: 100 },
    obstacles: [
      // All 4 corner blockers
      ...cornerBlockerNW(),
      ...cornerBlockerNE(),
      ...cornerBlockerSE(),
      ...cornerBlockerSW(),

      // Central hashtag pattern — forces zig-zag navigation
      wall(0, 0, 80, 6, 18),      // horizontal centre bar
      wall(40, 40, 6, 80, 18),     // vertical NE bar
      wall(-40, -40, 6, 80, 18),  // vertical SW bar
      wall(0, 80, 80, 6, 18),     // horizontal north bar
      wall(0, -80, 80, 6, 18),    // horizontal south bar

      // Dead-end traps — look like corridors but are blocked by corner blockers
      wall(80, 0, 6, 80, 18),      // east dead-end (blocked by NE/SE corner blockers)
      wall(-80, 0, 6, 80, 18),     // west dead-end (blocked by NW/SW corner blockers)

      // Crates scattered in the quadrants
      { x: 60, z: 60, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: -60, z: 60, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: 60, z: -60, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: -60, z: -60, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: 0, z: 60, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: 0, z: -60, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: 60, z: 0, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: -60, z: 0, width: 12, height: 12, depth: 12, type: 'crate' },

      // Ramps for visual variety and slight navigation challenge
      { x: 80, z: 80, width: 20, height: 5, depth: 20, type: 'ramp', rampAngle: 0.3 },
      { x: -80, z: -80, width: 20, height: 5, depth: 20, type: 'ramp', rampAngle: -0.3 },

      // Industrial stacks — tall obstacles that block sight lines
      { x: 80, z: -80, width: 20, height: 30, depth: 20, type: 'stack' },
      { x: -80, z: 80, width: 20, height: 30, depth: 20, type: 'stack' },
    ]
  },
];
