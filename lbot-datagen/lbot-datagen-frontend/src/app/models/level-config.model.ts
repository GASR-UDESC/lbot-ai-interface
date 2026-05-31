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
 *  - Level 1 (Armazem)  : Z-shaped forced path using walls. Solvable with D+R only.
 *  - Level 2 (Escritorio): Snake/weave corridor with vertical barriers. Solvable with D+R only.
 *  - Level 3 (Cidade)   : Chicane with staggered walls forcing S-curve navigation. Requires arcs.
 *  - Level 4 (Floresta) : Circular arena with dense tree clusters. Requires arcs.
 *  - Level 5 (Fabrica)  : Dense wall barrier with ramp bridge. Requires ramp usage.
 */
export const LEVEL_CONFIGS: LevelConfig[] = [
  // ─────────────────────────────────────────────
  // Level 1 — Armazem (Warehouse)
  // Z-shaped path: go right → gap → go up → go left → gap → go up to goal
  // Solvable with D+R only (at least 4 direction changes)
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
    startPoint: { x: -170, z: -170 },
    goalPoint:  { x: 170, z: 170 },
    arenaShape: 'square',
    arenaSize: { width: 400, height: 400 },
    obstacles: [
      // Horizontal wall #1 at z=-30, blocks left-to-center. Gap on right side (x > 80).
      { x: -60, z: -30, width: 80, height: 18, depth: 12, type: 'wall' },
      { x:  20, z: -30, width: 80, height: 18, depth: 12, type: 'wall' },
      // Vertical extension connecting wall #1 to left arena edge
      { x: -150, z: -30, width: 60, height: 18, depth: 12, type: 'wall' },
      // Horizontal wall #2 at z=70, blocks center-to-right. Gap on left side (x < -80).
      { x:  60, z:  70, width: 80, height: 18, depth: 12, type: 'wall' },
      { x: -20, z:  70, width: 80, height: 18, depth: 12, type: 'wall' },
      // Vertical extension connecting wall #2 to right arena edge
      { x: 150, z:  70, width: 60, height: 18, depth: 12, type: 'wall' },
      // Crates to add visual interest and tighten the Z-path
      { x: 130, z: -100, width: 20, height: 15, depth: 20, type: 'crate' },
      { x: -130, z: 130, width: 20, height: 15, depth: 20, type: 'crate' },
      { x:   0, z:  20, width: 15, height: 12, depth: 15, type: 'crate' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 2 — Escritorio (Office)
  // Snake pattern: vertical walls with alternating gaps force weaving path
  // Solvable with D+R only (6+ direction changes)
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
    startPoint: { x: -210, z: -110 },
    goalPoint:  { x: 210, z: 110 },
    arenaShape: 'rectangle',
    arenaSize: { width: 500, height: 300 },
    obstacles: [
      // Vertical barrier #1 at x=-100, gap at bottom (z < -60)
      { x: -100, z:  30, width: 12, height: 15, depth: 80, type: 'wall' },
      { x: -100, z: 100, width: 12, height: 15, depth: 60, type: 'wall' },
      // Vertical barrier #2 at x=0, gap at top (z > 60)
      { x:   0, z: -30, width: 12, height: 15, depth: 80, type: 'wall' },
      { x:   0, z: -100, width: 12, height: 15, depth: 60, type: 'wall' },
      // Vertical barrier #3 at x=100, gap at bottom (z < -60)
      { x: 100, z:  30, width: 12, height: 15, depth: 80, type: 'wall' },
      { x: 100, z: 100, width: 12, height: 15, depth: 60, type: 'wall' },
      // Desk crates adding office atmosphere
      { x: -180, z:  80, width: 18, height: 10, depth: 18, type: 'crate' },
      { x:  50, z: -110, width: 18, height: 10, depth: 18, type: 'crate' },
      { x: 180, z: -60, width: 18, height: 10, depth: 18, type: 'crate' },
      { x: -50, z: 110, width: 18, height: 10, depth: 18, type: 'crate' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 3 — Cidade (City)
  // Chicane: staggered walls creating tight S-curve passages.
  // Arc commands (A) strongly encouraged — narrow gaps between offset walls
  // require curved navigation for efficient traversal.
  // ─────────────────────────────────────────────
  {
    id: 3,
    name: 'Cidade',
    theme: {
      groundColor: '#4A4A4A',
      wallColor:   '#333333',
      obstacleColor: '#666666',
      skyColor:    '#708090'
    },
    startPoint: { x: -180, z: -180 },
    goalPoint:  { x: 180, z: 180 },
    arenaShape: 'square',
    arenaSize: { width: 450, height: 450 },
    obstacles: [
      // Chicane walls — staggered horizontal barriers with narrow offset gaps
      // The gaps are offset left-right so straight D+R paths get blocked.
      // Wall row 1 (bottom): gap on right side
      { x: -60, z: -100, width: 80, height: 25, depth: 12, type: 'wall' },
      { x: -140, z: -100, width: 60, height: 25, depth: 12, type: 'wall' },
      // Wall row 2: gap on left side (offset from row 1)
      { x:  60, z: -40, width: 80, height: 25, depth: 12, type: 'wall' },
      { x: 140, z: -40, width: 60, height: 25, depth: 12, type: 'wall' },
      // Wall row 3: gap on right side
      { x: -40, z:  30, width: 80, height: 25, depth: 12, type: 'wall' },
      { x: -130, z:  30, width: 70, height: 25, depth: 12, type: 'wall' },
      // Wall row 4: gap on left side
      { x:  40, z: 100, width: 80, height: 25, depth: 12, type: 'wall' },
      { x: 130, z: 100, width: 70, height: 25, depth: 12, type: 'wall' },
      // Side walls preventing arena-edge bypass
      { x: -180, z: -40, width: 12, height: 25, depth: 100, type: 'wall' },
      { x:  180, z:  40, width: 12, height: 25, depth: 100, type: 'wall' },
      // Corner blockers forcing the S-curve path
      { x: 120, z: -150, width: 30, height: 20, depth: 30, type: 'crate' },
      { x: -120, z: 150, width: 30, height: 20, depth: 30, type: 'crate' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 4 — Floresta (Forest)
  // Circular arena with dense "tree" clusters blocking straight lines.
  // The circular boundary and obstacle density strongly encourage arc navigation.
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
    startPoint: { x: -120, z: -120 },
    goalPoint:  { x: 120, z: 120 },
    arenaShape: 'circle',
    arenaSize: { width: 400, height: 400 },
    obstacles: [
      // Central cluster — blocks the direct diagonal path entirely
      { x:   0, z:   0, width: 30, height: 28, depth: 30, type: 'crate' },
      { x: -30, z:  25, width: 25, height: 28, depth: 25, type: 'crate' },
      { x:  30, z: -25, width: 25, height: 28, depth: 25, type: 'crate' },
      { x:  25, z:  30, width: 20, height: 28, depth: 20, type: 'crate' },
      { x: -25, z: -30, width: 20, height: 28, depth: 20, type: 'crate' },
      // Mid-ring trees — block straight-line detours, force curved arcing
      { x: -85, z: -30, width: 18, height: 30, depth: 18, type: 'crate' },
      { x: -55, z:  70, width: 18, height: 30, depth: 18, type: 'crate' },
      { x:  30, z: -80, width: 18, height: 30, depth: 18, type: 'crate' },
      { x:  80, z:  40, width: 18, height: 30, depth: 18, type: 'crate' },
      // Outer ring trees — prevent wide arc bypasses
      { x: -110, z:  60, width: 20, height: 25, depth: 20, type: 'crate' },
      { x:  100, z: -70, width: 20, height: 25, depth: 20, type: 'crate' },
      { x:  70, z: 100, width: 20, height: 25, depth: 20, type: 'crate' },
      { x: -70, z: -100, width: 20, height: 25, depth: 20, type: 'crate' },
    ]
  },

  // ─────────────────────────────────────────────
  // Level 5 — Fabrica (Factory)
  // Dense wall cluster spanning the arena center with ramp bridges.
  // The ramps are the only efficient path over the barrier.
  // Requires climbing a ramp to reach the goal zone.
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
    startPoint: { x: -250, z: -150 },
    goalPoint:  { x: 250, z: 150 },
    arenaShape: 'rectangle',
    arenaSize: { width: 600, height: 400 },
    obstacles: [
      // Dense central barrier — multiple thick wall segments forming impassable band
      { x: -200, z:  0, width: 60, height: 20, depth: 50, type: 'wall' },
      { x: -130, z:  0, width: 60, height: 20, depth: 50, type: 'wall' },
      { x:  -60, z:  0, width: 60, height: 20, depth: 50, type: 'wall' },
      { x:   10, z:  0, width: 60, height: 20, depth: 50, type: 'wall' },
      { x:   80, z:  0, width: 60, height: 20, depth: 50, type: 'wall' },
      { x:  150, z:  0, width: 60, height: 20, depth: 50, type: 'wall' },
      { x:  220, z:  0, width: 60, height: 20, depth: 50, type: 'wall' },
      // Edge walls closing gaps at arena boundaries
      { x: -260, z:  0, width: 40, height: 20, depth: 50, type: 'wall' },
      { x:  270, z:  0, width: 40, height: 20, depth: 50, type: 'wall' },
      // Primary ramp (bridge over the barrier) — positioned for approach from start side
      { x: -30, z: -50, width: 50, height: 4, depth: 80, type: 'ramp', rampAngle: 0.35 },
      // Secondary ramp on the far side for approach variation
      { x: 120, z: -50, width: 45, height: 4, depth: 70, type: 'ramp', rampAngle: 0.30 },
      // Industrial crates adding complexity
      { x: -180, z: -100, width: 25, height: 15, depth: 25, type: 'crate' },
      { x:  200, z:  100, width: 25, height: 15, depth: 25, type: 'crate' },
      { x: -100, z:  120, width: 20, height: 15, depth: 20, type: 'crate' },
      { x:  100, z: -120, width: 20, height: 15, depth: 20, type: 'crate' },
    ]
  },
];
