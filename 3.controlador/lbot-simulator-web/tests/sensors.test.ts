import { describe, expect, it } from 'vitest';
import { computeProximity } from '../server/sensors.js';

describe('computeProximity', () => {
  it('center position facing north returns 200cm both ways', () => {
    const result = computeProximity(0, 0, 0);
    expect(result.frente).toBe(200);
    expect(result.tras).toBe(200);
  });

  it('center position facing east (rotation 90)', () => {
    const result = computeProximity(0, 0, 90);
    expect(result.frente).toBe(200);
    expect(result.tras).toBe(200);
  });

  it('center position facing south (rotation 180)', () => {
    const result = computeProximity(0, 0, 180);
    expect(result.frente).toBe(200);
    expect(result.tras).toBe(200);
  });

  it('center position facing west (rotation 270)', () => {
    const result = computeProximity(0, 0, 270);
    expect(result.frente).toBe(200);
    expect(result.tras).toBe(200);
  });

  it('near north wall facing north', () => {
    const result = computeProximity(0, 180, 0);
    expect(result.frente).toBe(20);
    expect(result.tras).toBe(380);
  });

  it('near south wall facing north', () => {
    const result = computeProximity(0, -180, 0);
    expect(result.frente).toBe(380);
    expect(result.tras).toBe(20);
  });

  it('near east wall facing east', () => {
    const result = computeProximity(180, 0, 90);
    expect(result.frente).toBe(20);
    expect(result.tras).toBe(380);
  });

  it('near west wall facing west', () => {
    const result = computeProximity(-180, 0, 270);
    expect(result.frente).toBe(20);
    expect(result.tras).toBe(380);
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
});
