import { ARENA_OBJECTS, getObjectAABB, type AABB } from '../shared/arena-objects.js';

const HALF_ARENA = 200;
const MAX_SENSOR_DISTANCE = 400;
const ROBOT_HALF_LENGTH = 15;

function degToRad(degrees: number): number {
  return (degrees * Math.PI) / 180;
}

function rayWallDistance(
  ox: number,
  oz: number,
  dx: number,
  dz: number,
): number {
  let minDist = Infinity;

  if (dx > 0.0001) {
    const t = (HALF_ARENA - ox) / dx;
    if (t > 0 && t < minDist) minDist = t;
  } else if (dx < -0.0001) {
    const t = (-HALF_ARENA - ox) / dx;
    if (t > 0 && t < minDist) minDist = t;
  }

  if (dz > 0.0001) {
    const t = (HALF_ARENA - oz) / dz;
    if (t > 0 && t < minDist) minDist = t;
  } else if (dz < -0.0001) {
    const t = (-HALF_ARENA - oz) / dz;
    if (t > 0 && t < minDist) minDist = t;
  }

  return minDist;
}

function rayAABBDistance(
  ox: number,
  oz: number,
  dx: number,
  dz: number,
  aabb: AABB,
): number {
  let tmin = -Infinity;
  let tmax = Infinity;

  if (Math.abs(dx) > 0.0001) {
    const tx1 = (aabb.minX - ox) / dx;
    const tx2 = (aabb.maxX - ox) / dx;
    tmin = Math.max(tmin, Math.min(tx1, tx2));
    tmax = Math.min(tmax, Math.max(tx1, tx2));
  } else {
    if (ox < aabb.minX || ox > aabb.maxX) {
      return Infinity;
    }
  }

  if (Math.abs(dz) > 0.0001) {
    const tz1 = (aabb.minZ - oz) / dz;
    const tz2 = (aabb.maxZ - oz) / dz;
    tmin = Math.max(tmin, Math.min(tz1, tz2));
    tmax = Math.min(tmax, Math.max(tz1, tz2));
  } else {
    if (oz < aabb.minZ || oz > aabb.maxZ) {
      return Infinity;
    }
  }

  if (tmax >= tmin && tmax > 0) {
    return tmin > 0 ? tmin : tmax;
  }

  return Infinity;
}

function rayClosestDistance(
  ox: number,
  oz: number,
  dx: number,
  dz: number,
): number {
  let minDist = rayWallDistance(ox, oz, dx, dz);

  for (const obj of ARENA_OBJECTS) {
    const aabb = getObjectAABB(obj);
    const dist = rayAABBDistance(ox, oz, dx, dz, aabb);
    if (dist < minDist) {
      minDist = dist;
    }
  }

  return minDist;
}

export function computeProximity(
  x: number,
  z: number,
  rotationDeg: number,
): { frente: number; tras: number } {
  const rad = degToRad(rotationDeg);
  const frontDx = Math.sin(rad);
  const frontDz = Math.cos(rad);

  let frente = rayClosestDistance(x, z, frontDx, frontDz) - ROBOT_HALF_LENGTH;
  frente = Math.max(0, Math.min(frente, MAX_SENSOR_DISTANCE));

  let tras = rayClosestDistance(x, z, -frontDx, -frontDz) - ROBOT_HALF_LENGTH;
  tras = Math.max(0, Math.min(tras, MAX_SENSOR_DISTANCE));

  return { frente: Math.round(frente * 100) / 100, tras: Math.round(tras * 100) / 100 };
}
