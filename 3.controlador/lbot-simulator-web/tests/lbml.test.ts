import { describe, expect, it } from 'vitest';
import {
  formatParsedCommand,
  normalizeLbml,
  parseLbmlCommand,
  parseLbmlSequence,
  validateLbml,
} from '../shared/lbml.js';

describe('lbml helpers', () => {
  it('normalizes whitespace and casing', () => {
    expect(normalizeLbml(' d40f; r90l; ')).toBe('D40F;R90L;');
  });

  it('validates full sequences', () => {
    expect(validateLbml('D40F;R90L;D20F;')).toBe(true);
    expect(validateLbml('10F;')).toBe(false);
  });

  it('parses a single command', () => {
    expect(parseLbmlCommand('R90L;')).toEqual({ type: 'R', value: 90, direction: 'L' });
  });

  it('rejects invalid direction combinations', () => {
    expect(parseLbmlCommand('R90F;')).toBeNull();
  });

  it('parses a complete sequence', () => {
    expect(parseLbmlSequence('D40F;R90L;')).toEqual([
      { type: 'D', value: 40, direction: 'F' },
      { type: 'R', value: 90, direction: 'L' },
    ]);
  });

  it('formats parsed commands', () => {
    expect(formatParsedCommand({ type: 'D', value: 20, direction: 'B' })).toBe('D20B');
  });
});
