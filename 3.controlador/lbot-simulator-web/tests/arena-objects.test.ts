import { describe, expect, it } from 'vitest';
import {
  ARENA_OBJECTS,
  getObjectAABB,
  isPositionInsideArena,
  validateAndClampPosition,
} from '../shared/arena-objects.js';

describe('getObjectAABB', () => {
  it('returns correct AABB for a cube 15x15x15', () => {
    const cube = ARENA_OBJECTS.find((o) => o.id === 'cube-red')!;
    const aabb = getObjectAABB(cube);
    expect(aabb.minX).toBe(-157.5);
    expect(aabb.maxX).toBe(-142.5);
    expect(aabb.minZ).toBe(-157.5);
    expect(aabb.maxZ).toBe(-142.5);
  });

  it('returns correct AABB for a sphere with radius 10', () => {
    const sphere = ARENA_OBJECTS.find((o) => o.id === 'sphere-blue')!;
    const aabb = getObjectAABB(sphere);
    expect(aabb.minX).toBe(140);
    expect(aabb.maxX).toBe(160);
    expect(aabb.minZ).toBe(-110);
    expect(aabb.maxZ).toBe(-90);
  });

  it('returns correct approximate AABB for a cone (base 10, height 15)', () => {
    const cone = ARENA_OBJECTS.find((o) => o.id === 'cone-orange')!;
    const aabb = getObjectAABB(cone);
    expect(aabb.minX).toBe(170);
    expect(aabb.maxX).toBe(190);
    expect(aabb.minZ).toBe(170);
    expect(aabb.maxZ).toBe(190);
  });
});

describe('isPositionInsideArena', () => {
  it('returns true for a valid position (-150, -150)', () => {
    expect(isPositionInsideArena(-150, -150)).toBe(true);
  });

  it('returns false for an invalid position (250, 250)', () => {
    expect(isPositionInsideArena(250, 250)).toBe(false);
  });

  it('returns true for boundary position (200, 200)', () => {
    expect(isPositionInsideArena(200, 200)).toBe(true);
  });

  it('returns false for position just outside boundary (201, 0)', () => {
    expect(isPositionInsideArena(201, 0)).toBe(false);
  });
});

describe('validateAndClampPosition', () => {
  it('reposiciona posicao fora da arena', () => {
    const result = validateAndClampPosition(250, 250);
    expect(result.x).toBeLessThanOrEqual(200);
    expect(result.z).toBeLessThanOrEqual(200);
    expect(isPositionInsideArena(result.x, result.z)).toBe(true);
  });

  it('reposiciona posicao sobreposta ao robo (0, 0)', () => {
    const result = validateAndClampPosition(0, 0);
    const dist = Math.sqrt(result.x * result.x + result.z * result.z);
    expect(dist).toBeGreaterThanOrEqual(30);
    expect(isPositionInsideArena(result.x, result.z)).toBe(true);
  });

  it('reposiciona posicao parcialmente sobreposta ao robo (10, 10)', () => {
    const result = validateAndClampPosition(10, 10);
    const dist = Math.sqrt(result.x * result.x + result.z * result.z);
    expect(dist).toBeCloseTo(30, 5);
    expect(isPositionInsideArena(result.x, result.z)).toBe(true);
  });

  it('mantem posicao valida longe do robo', () => {
    const result = validateAndClampPosition(-150, -150);
    expect(result.x).toBe(-150);
    expect(result.z).toBe(-150);
  });
});
