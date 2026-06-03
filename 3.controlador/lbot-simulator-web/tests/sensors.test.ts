import { describe, expect, it } from 'vitest';
import { computeProximity } from '../server/sensors.js';

describe('computeProximity', () => {
  it('center position facing north returns 200cm/170cm', () => {
    const result = computeProximity(0, 0, 0);
    expect(result.frente).toBe(200); // wall north
    expect(result.tras).toBe(170);   // sphere-green AABB edge
  });

  it('center position facing east (rotation 90)', () => {
    const result = computeProximity(0, 0, 90);
    expect(result.frente).toBe(200); // wall east
    expect(result.tras).toBe(172.5); // cube-purple AABB edge
  });

  it('center position facing south (rotation 180)', () => {
    const result = computeProximity(0, 0, 180);
    expect(result.frente).toBe(170); // sphere-green AABB edge
    expect(result.tras).toBe(200);   // wall south
  });

  it('center position facing west (rotation 270)', () => {
    const result = computeProximity(0, 0, 270);
    expect(result.frente).toBe(172.5); // cube-purple AABB edge
    expect(result.tras).toBe(200);     // wall west
  });

  it('near north wall facing north', () => {
    const result = computeProximity(0, 180, 0);
    expect(result.frente).toBe(20);  // wall north
    expect(result.tras).toBe(350);   // sphere-green AABB edge
  });

  it('near south wall facing north', () => {
    const result = computeProximity(0, -180, 0);
    expect(result.frente).toBe(10); // inside sphere-green AABB (closest edge forward)
    expect(result.tras).toBe(10);   // inside sphere-green AABB (closest edge backward)
  });

  it('near east wall facing east', () => {
    const result = computeProximity(180, 0, 90);
    expect(result.frente).toBe(20);   // wall east
    expect(result.tras).toBe(352.5);  // cube-purple AABB edge
  });

  it('near west wall facing west', () => {
    const result = computeProximity(-180, 0, 270);
    expect(result.frente).toBe(7.5);  // inside cube-purple AABB (closest edge forward)
    expect(result.tras).toBe(7.5);    // inside cube-purple AABB (closest edge backward)
  });

  it('corner position facing 45 degrees', () => {
    const result = computeProximity(180, 180, 45);
    expect(result.frente).toBeGreaterThan(0);
    expect(result.frente).toBeLessThan(400);
    expect(result.tras).toBeGreaterThan(0);
  });

  it('halfway position', () => {
    const result = computeProximity(100, 0, 0);
    expect(result.frente).toBe(200);
    expect(result.tras).toBe(200);
  });

  it('caps at MAX_SENSOR_DISTANCE (400cm)', () => {
    const result = computeProximity(0, 0, 0);
    expect(result.frente).toBeLessThanOrEqual(400);
    expect(result.tras).toBeLessThanOrEqual(400);
  });

  it('detects object in front (sphere-green at 0,-180)', () => {
    // Robot at (0, -100) facing south (180°)
    // Sphere-green AABB: z from -190 to -170
    // Ray from (0,-100) with dz=-1 hits AABB at t=70 (closest edge)
    // Wall south is at z=-200, distance = 100
    // Object is closer, so sensor should report ~70
    const result = computeProximity(0, -100, 180);
    expect(result.frente).toBe(70);
  });

  it('detects object behind (cube-red at -150,-150)', () => {
    // Robot at (-150, -100) facing north (0°)
    // Cube-red AABB: z from -157.5 to -142.5
    // Ray behind (dz=-1) from (-150,-100) hits AABB at t=42.5 (closest edge)
    // Wall south is at z=-200, distance = 100
    const result = computeProximity(-150, -100, 0);
    expect(result.tras).toBe(42.5);
  });

  it('prefers closer object over wall (cube-purple at -180,0)', () => {
    // Robot at (-160, 0) facing west (270°)
    // Cube-purple AABB: x from -187.5 to -172.5
    // Ray west (dx=-1) from (-160,0) hits AABB at t=12.5 (closest edge at x=-172.5)
    // Wall west is at x=-200, distance = 40
    const result = computeProximity(-160, 0, 270);
    expect(result.frente).toBe(12.5);
  });

  it('no object in range returns wall distance', () => {
    // Robot at (0, 0) facing north (0°)
    // No object directly north; wall north at z=200
    const result = computeProximity(0, 0, 0);
    expect(result.frente).toBe(200);
  });
});
