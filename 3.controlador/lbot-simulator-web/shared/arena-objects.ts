export type ArenaObjectType = 'cube' | 'sphere' | 'cone';

export interface CubeSize {
  width: number;
  height: number;
  depth: number;
}

export interface SphereSize {
  radius: number;
}

export interface ConeSize {
  radius: number;
  height: number;
}

export type ObjectSize = CubeSize | SphereSize | ConeSize;

export interface ArenaObject {
  id: string;
  type: ArenaObjectType;
  x: number;
  z: number;
  color: string;
  size: ObjectSize;
}

export interface PhysicalWall {
  x: number;
  z: number;
  width: number;
  depth: number;
  height: number;
}

export const ARENA_OBJECTS: ArenaObject[] = [
  {
    id: 'cube-red',
    type: 'cube',
    x: -150,
    z: -150,
    color: '#ff0000',
    size: { width: 15, height: 15, depth: 15 },
  },
  {
    id: 'sphere-blue',
    type: 'sphere',
    x: 150,
    z: -100,
    color: '#0000ff',
    size: { radius: 10 },
  },
  {
    id: 'cube-yellow',
    type: 'cube',
    x: -100,
    z: 150,
    color: '#ffff00',
    size: { width: 15, height: 15, depth: 15 },
  },
  {
    id: 'cone-orange',
    type: 'cone',
    x: 180,
    z: 180,
    color: '#ffa500',
    size: { radius: 10, height: 15 },
  },
  {
    id: 'sphere-green',
    type: 'sphere',
    x: 0,
    z: -180,
    color: '#00ff00',
    size: { radius: 10 },
  },
  {
    id: 'cube-purple',
    type: 'cube',
    x: -180,
    z: 0,
    color: '#800080',
    size: { width: 15, height: 15, depth: 15 },
  },
];

export const PHYSICAL_WALLS: PhysicalWall[] = [
  // North
  { x: 0, z: 204, width: 408, depth: 8, height: 30 },
  // South
  { x: 0, z: -204, width: 408, depth: 8, height: 30 },
  // East
  { x: 204, z: 0, width: 8, depth: 400, height: 30 },
  // West
  { x: -204, z: 0, width: 8, depth: 400, height: 30 },
];

export interface AABB {
  minX: number;
  maxX: number;
  minZ: number;
  maxZ: number;
}

export function getObjectAABB(object: ArenaObject): AABB {
  const { x, z, type, size } = object;

  if (type === 'cube') {
    const s = size as CubeSize;
    const halfW = s.width / 2;
    const halfD = s.depth / 2;
    return {
      minX: x - halfW,
      maxX: x + halfW,
      minZ: z - halfD,
      maxZ: z + halfD,
    };
  }

  if (type === 'sphere') {
    const s = size as SphereSize;
    const r = s.radius;
    return {
      minX: x - r,
      maxX: x + r,
      minZ: z - r,
      maxZ: z + r,
    };
  }

  // cone
  const s = size as ConeSize;
  const r = s.radius;
  return {
    minX: x - r,
    maxX: x + r,
    minZ: z - r,
    maxZ: z + r,
  };
}

export function isPositionInsideArena(x: number, z: number): boolean {
  const LIMIT = 200;
  return x >= -LIMIT && x <= LIMIT && z >= -LIMIT && z <= LIMIT;
}

export function validateAndClampPosition(x: number, z: number): { x: number; z: number } {
  const LIMIT = 200;
  const ROBOT_SPAWN_RADIUS = 30;

  let clampedX = Math.max(-LIMIT, Math.min(LIMIT, x));
  let clampedZ = Math.max(-LIMIT, Math.min(LIMIT, z));

  const dx = clampedX;
  const dz = clampedZ;
  const dist = Math.sqrt(dx * dx + dz * dz);

  if (dist < ROBOT_SPAWN_RADIUS && dist > 0) {
    const scale = ROBOT_SPAWN_RADIUS / dist;
    clampedX = dx * scale;
    clampedZ = dz * scale;
  } else if (dist === 0) {
    // If exactly at (0,0), push to a safe default position
    clampedX = ROBOT_SPAWN_RADIUS;
    clampedZ = 0;
  }

  return { x: clampedX, z: clampedZ };
}
