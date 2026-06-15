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
// Helper to build horizontal maze walls (long walls on X axis)
// ---------------------------------------------------------------------------
function hWall(x: number, z: number, width: number, height = 18, depth = 6): ObstacleConfig {
  return { x, z, width, height, depth, type: 'wall' };
}

// ---------------------------------------------------------------------------
// Helper to build vertical maze walls (long walls on Z axis)
// ---------------------------------------------------------------------------
function vWall(x: number, z: number, depth: number, height = 18, width = 6): ObstacleConfig {
  return { x, z, width, height, depth, type: 'wall' };
}

// ---------------------------------------------------------------------------
// Helper to build a corner blocker (L-shaped inner wall near arena border)
// ---------------------------------------------------------------------------
function cornerBlockerNE(): ObstacleConfig[] {
  return [
    vWall(130, 60, 80, 15, 6),
    hWall(60, 130, 80, 15, 6),
  ];
}
function cornerBlockerNW(): ObstacleConfig[] {
  return [
    vWall(-130, 60, 80, 15, 6),
    hWall(-60, 130, 80, 15, 6),
  ];
}
function cornerBlockerSE(): ObstacleConfig[] {
  return [
    vWall(130, -60, 80, 15, 6),
    hWall(60, -130, 80, 15, 6),
  ];
}
function cornerBlockerSW(): ObstacleConfig[] {
  return [
    vWall(-130, -60, 80, 15, 6),
    hWall(-60, -130, 80, 15, 6),
  ];
}

// ---------------------------------------------------------------------------
// Maze grid helpers — segments of 100 units, leaving intentional gaps
// ---------------------------------------------------------------------------

/** Horizontal maze-barrier segment (runs along X) */
function mazeH(z: number, x: number, w = 100, h = 18, d = 6): ObstacleConfig {
  return { x, z, width: w, height: h, depth: d, type: 'wall' };
}

/** Vertical maze-barrier segment (runs along Z) */
function mazeV(x: number, z: number, d = 100, h = 18, w = 6): ObstacleConfig {
  return { x, z, width: w, height: h, depth: d, type: 'wall' };
}

/**
 * Definitions for all 5 game levels.
 *
 * Design philosophy (maze-only, no ramps):
 *  - Nivel 1 (Tutorial)  : sparse crates, open path. Learn controls.
 *  - Nivel 2 (Entrar)   : start outside, goal inside. Corner blockers + maze.
 *  - Nivel 3 (Sair)     : start inside, goal outside. Corner blockers + maze.
 *  - Nivel 4 (Atravessar): full diagonal with 4 corner blockers. No border access.
 *  - Nivel 5 (Complexo)  : mirrored diagonal with dead ends. Most confusing.
 */
export const LEVEL_CONFIGS: LevelConfig[] = [
  // ═══════════════════════════════════════════════════════════════════════
  // Level 1 — Nivel 1 (Tutorial)
  // Start: (-150,-150)  Goal: (150,150)
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
    startPoint: { x: -150, z: -150 },
    goalPoint: { x: 150, z: 150 },
    obstacles: [
      // Central vertical wall — forces the player to go around
      vWall(0, 0, 120, 18, 6),
      // Some crates to add visual interest
      { x: -40, z: 40, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: 40, z: -40, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: 0, z: 80, width: 12, height: 12, depth: 12, type: 'crate' },
      { x: 0, z: -80, width: 12, height: 12, depth: 12, type: 'crate' },
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════
  // Level 2 — Nivel 2 (Entrar)
  // Start: (-150,-150)  Goal: (50,50)
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
    startPoint: { x: -150, z: -150 },
    goalPoint: { x: 50, z: 50 },
    obstacles: [
      // ── Corner blockers (confine start corner) ──
      vWall(-150, -90, 60, 18, 6),   // west side, blocks going up along border
      hWall(-90, -150, 60, 18, 6),   // south side, blocks going right along border

      // ── Maze grid walls (horizontal lines at z = -100, 0, 100) ──
      // z = -100: gap at x = -150 (correct path goes up)
      mazeH(-100, -50, 100),
      mazeH(-100, 50, 100),
      mazeH(-100, 150, 100),

      // z = 0: gap at x = -50 (correct path goes right)
      mazeH(0, -150, 100),
      mazeH(0, 50, 100),
      mazeH(0, 150, 100),

      // z = 100: gap at x = 50 (correct path goes up)
      mazeH(100, -150, 100),
      mazeH(100, -50, 100),
      mazeH(100, 150, 100),

      // ── Maze grid walls (vertical lines at x = -100, 0, 100) ──
      // x = -100: gap at z = -50 (correct path goes right)
      mazeV(-100, -150, 100),
      mazeV(-100, 50, 100),
      mazeV(-100, 150, 100),

      // x = 0: gap at z = 50 (correct path goes up)
      mazeV(0, -150, 100),
      mazeV(0, -50, 100),
      mazeV(0, 150, 100),

      // x = 100: gap at z = 150 (correct path goes right toward goal)
      mazeV(100, -150, 100),
      mazeV(100, -50, 100),
      mazeV(100, 50, 100),

      // ── Goal corner blockers (seal the goal area) ──
      vWall(50, 100, 60, 15, 6),
      hWall(100, 50, 60, 15, 6),
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════
  // Level 3 — Nivel 3 (Sair)
  // Start: (50,50)  Goal: (150,150)
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
    startPoint: { x: 50, z: 50 },
    goalPoint: { x: 150, z: 150 },
    obstacles: [
      // ── Corner blockers (seal the goal corner) ──
      vWall(150, 90, 60, 15, 6),
      hWall(90, 150, 60, 15, 6),

      // ── Corner blockers (confine start area) ──
      vWall(0, 0, 60, 15, 6),
      hWall(0, 0, 60, 15, 6),

      // ── Maze grid walls (horizontal lines at z = -100, 0, 100) ──
      // z = -100: gap at x = 50 (path goes down)
      mazeH(-100, -150, 100),
      mazeH(-100, -50, 100),
      mazeH(-100, 150, 100),

      // z = 0: gap at x = 150 (path goes down)
      mazeH(0, -150, 100),
      mazeH(0, -50, 100),
      mazeH(0, 50, 100),

      // z = 100: gap at x = 50 (path goes up)
      mazeH(100, -150, 100),
      mazeH(100, -50, 100),
      mazeH(100, 150, 100),

      // ── Maze grid walls (vertical lines at x = -100, 0, 100) ──
      // x = -100: gap at z = -150 (path goes right)
      mazeV(-100, -50, 100),
      mazeV(-100, 50, 100),
      mazeV(-100, 150, 100),

      // x = 0: gap at z = -50 (path goes right)
      mazeV(0, -150, 100),
      mazeV(0, 50, 100),
      mazeV(0, 150, 100),

      // x = 100: gap at z = 50 (path goes up)
      mazeV(100, -150, 100),
      mazeV(100, -50, 100),
      mazeV(100, 150, 100),
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════
  // Level 4 — Nivel 4 (Atravessar)
  // Start: (-150,150)  Goal: (150,-150)
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
    startPoint: { x: -150, z: 150 },
    goalPoint: { x: 150, z: -150 },
    obstacles: [
      // ── All 4 corner blockers (no border access) ──
      ...cornerBlockerNW(),
      ...cornerBlockerNE(),
      ...cornerBlockerSE(),
      ...cornerBlockerSW(),

      // ── Maze grid walls (horizontal lines at z = -100, 0, 100) ──
      // z = -100: gap at x = 50 (path goes down toward goal)
      mazeH(-100, -150, 100),
      mazeH(-100, -50, 100),
      mazeH(-100, 150, 100),

      // z = 0: gap at x = -50 (path goes down)
      mazeH(0, -150, 100),
      mazeH(0, 50, 100),
      mazeH(0, 150, 100),

      // z = 100: gap at x = -150 (path goes down from start)
      mazeH(100, -50, 100),
      mazeH(100, 50, 100),
      mazeH(100, 150, 100),

      // ── Maze grid walls (vertical lines at x = -100, 0, 100) ──
      // x = -100: gap at z = 50 (path goes right)
      mazeV(-100, -150, 100),
      mazeV(-100, -50, 100),
      mazeV(-100, 150, 100),

      // x = 0: gap at z = -50 (path goes right)
      mazeV(0, -150, 100),
      mazeV(0, 50, 100),
      mazeV(0, 150, 100),

      // x = 100: gap at z = -150 (path goes right toward goal)
      mazeV(100, -50, 100),
      mazeV(100, 50, 100),
      mazeV(100, 150, 100),
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════
  // Level 5 — Nivel 5 (Complexo)
  // Start: (150,-150)  Goal: (-150,150)
  // Mirrored diagonal + dead ends
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
    startPoint: { x: 150, z: -150 },
    goalPoint: { x: -150, z: 150 },
    obstacles: [
      // ── All 4 corner blockers (no border access) ──
      ...cornerBlockerNW(),
      ...cornerBlockerNE(),
      ...cornerBlockerSE(),
      ...cornerBlockerSW(),

      // ── Maze grid walls (horizontal lines at z = -100, 0, 100) ──
      // z = -100: gap at x = 150 (path goes up from start)
      mazeH(-100, -50, 100),
      mazeH(-100, 50, 100),
      mazeH(-100, 150, 100),

      // z = 0: gap at x = 50 (path goes up)
      mazeH(0, -150, 100),
      mazeH(0, -50, 100),
      mazeH(0, 150, 100),

      // z = 100: gap at x = -50 (path goes up)
      mazeH(100, -150, 100),
      mazeH(100, 50, 100),
      mazeH(100, 150, 100),

      // ── Maze grid walls (vertical lines at x = -100, 0, 100) ──
      // x = -100: gap at z = 150 (path goes left toward goal)
      mazeV(-100, -150, 100),
      mazeV(-100, -50, 100),
      mazeV(-100, 50, 100),

      // x = 0: gap at z = 50 (path goes left)
      mazeV(0, -150, 100),
      mazeV(0, -50, 100),
      mazeV(0, 150, 100),

      // x = 100: gap at z = -50 (path goes left)
      mazeV(100, -150, 100),
      mazeV(100, 50, 100),
      mazeV(100, 150, 100),

      // ── Dead-end traps (extra walls that close off tempting fake paths) ──
      // Fake path at (-50, 50) — looks like a corridor but leads nowhere
      hWall(-50, 50, 40, 15, 6),
      // Fake path at (50, -50) — dead end
      vWall(50, -50, 40, 15, 6),
      // Shortcut blocker
      vWall(-50, -50, 40, 18, 6),
      hWall(-50, -50, 40, 18, 6),
    ]
  },
];
