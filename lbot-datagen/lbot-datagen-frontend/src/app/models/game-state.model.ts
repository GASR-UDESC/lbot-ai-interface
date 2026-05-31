/**
 * Represents the current phase of the game.
 * - idle: no active run (menu / not started)
 * - playing: a level is in progress and the timer is running
 * - level-complete: a level was just finished; transition screen is showing
 * - run-complete: all 5 levels were finished; victory screen is showing
 */
export type GamePhase = 'idle' | 'playing' | 'level-complete' | 'run-complete';

/**
 * Tracks the progress of an individual level inside a run.
 */
export interface LevelProgress {
  /** Level identifier (1-5) */
  levelId: number;
  /** Time taken to complete this level in milliseconds */
  timeMs: number;
  /** Whether the level was completed */
  completed: boolean;
}

/**
 * Represents the full state of an active (or just finished) game run.
 */
export interface RunState {
  /** The level the player is currently on (1-5) */
  currentLevel: number;
  /** Current phase of the game flow */
  phase: GamePhase;
  /** Accumulated time for each completed level (ms), in order */
  levelTimes: number[];
  /** Sum of all completed level times in milliseconds */
  totalTimeMs: number;
  /** Whether a run is currently in progress */
  isRunActive: boolean;
}
