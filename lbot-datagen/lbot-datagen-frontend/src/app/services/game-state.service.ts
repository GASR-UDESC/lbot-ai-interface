import { Injectable, computed, signal } from '@angular/core';
import { GamePhase } from '../models/game-state.model';

/**
 * Manages all game-run state using Angular Signals.
 *
 * Responsibilities:
 * - Track the current level (1-5), game phase, per-level times, and full run time.
 * - Provide a wall-clock timer based on Date.now() (no drift).
 * - Expose reactive signals / computed values for UI consumption.
 *
 * Intentionally NOT directly tied to Angular's change-detection loop so
 * it can be called from outside-zone code (e.g. the render loop) and from
 * regular template bindings alike.
 */
@Injectable({ providedIn: 'root' })
export class GameStateService {
  // ─────────────────────────────────────────────────────────────────────────
  // Core signals
  // ─────────────────────────────────────────────────────────────────────────

  /** Current phase of the game flow. */
  readonly phase = signal<GamePhase>('idle');

  /** Level the player is currently on (1-5). */
  readonly currentLevel = signal<number>(1);

  /** Completed level times in ms, one entry per finished level. */
  readonly levelTimes = signal<number[]>([]);

  /** Timestamp (Date.now()) when the current level started. */
  readonly currentLevelStartTime = signal<number>(0);

  /** Timestamp (Date.now()) when the current run started. */
  readonly runStartTime = signal<number>(0);

  /** Whether a run is currently active. */
  readonly isRunActive = signal<boolean>(false);

  // ─────────────────────────────────────────────────────────────────────────
  // Derived / computed signals
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Total elapsed time across ALL completed levels (sum of levelTimes).
   * Does not include the current, still-running level.
   */
  readonly totalElapsed = computed(() =>
    this.levelTimes().reduce((acc, t) => acc + t, 0)
  );

  /** True when the player is on the last level. */
  readonly isLastLevel = computed(() => this.currentLevel() === 5);

  // ─────────────────────────────────────────────────────────────────────────
  // Public methods
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Starts a brand-new run from level 1.
   * Resets all accumulated state and begins the timer for level 1.
   */
  startRun(): void {
    this.levelTimes.set([]);
    this.currentLevel.set(1);
    this.isRunActive.set(true);
    this.phase.set('playing');
    this.runStartTime.set(Date.now());
    this.startLevel();
  }

  /**
   * Records the start timestamp for the current level.
   * Called automatically by startRun() and nextLevel().
   */
  startLevel(): void {
    this.currentLevelStartTime.set(Date.now());
  }

  /**
   * Marks the current level as complete:
   * - Calculates the elapsed time for this level.
   * - Appends it to levelTimes.
   * - Sets phase to 'level-complete' (or 'run-complete' for the last level).
   */
  completeLevel(): void {
    const elapsed = this.isLastLevel()
      ? this.getGlobalElapsedMs() - this.levelTimes().reduce((acc, t) => acc + t, 0)
      : Date.now() - this.currentLevelStartTime();

    this.levelTimes.update(times => [...times, elapsed]);

    if (this.isLastLevel()) {
      this.phase.set('run-complete');
    } else {
      this.phase.set('level-complete');
    }
  }

  /**
   * Advances to the next level.
   * Should only be called when phase === 'level-complete'.
   * Increments currentLevel, resets to 'playing', and starts the level timer.
   */
  nextLevel(): void {
    if (this.currentLevel() < 5) {
      this.currentLevel.update(l => l + 1);
      this.phase.set('playing');
      this.startLevel();
    }
  }

  /**
   * Resets all state back to the initial idle condition.
   */
  resetRun(): void {
    this.phase.set('idle');
    this.currentLevel.set(1);
    this.levelTimes.set([]);
    this.currentLevelStartTime.set(0);
    this.runStartTime.set(0);
    this.isRunActive.set(false);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Timer helpers
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Returns the number of milliseconds elapsed in the *current* level.
   * Based on Date.now() so it has no drift and does not pause on reset.
   * Call this from the template / animation loop for a live display.
   */
  getElapsedMs(): number {
    const start = this.currentLevelStartTime();
    if (start === 0) return 0;
    return Date.now() - start;
  }

  /** Returns the milliseconds elapsed since the current run started. */
  getGlobalElapsedMs(): number {
    const start = this.runStartTime();
    if (start === 0) return 0;
    return Date.now() - start;
  }

  /**
   * Converts a millisecond value to "MM:SS" format.
   *
   * @example
   * formatTime(92000) // "01:32"
   * formatTime(5000)  // "00:05"
   */
  formatTime(ms: number): string {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }
}
