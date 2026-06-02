/**
 * Request payload for creating a new game run entry in the leaderboard.
 */
export interface CreateGameRunRequest {
  nickname: string;
  level1TimeMs: number;
  level2TimeMs: number;
  level3TimeMs: number;
  level4TimeMs: number;
  level5TimeMs: number;
}

/**
 * Response DTO for a game run entry returned by the backend.
 */
export interface GameRunResponse {
  id: string;
  nickname: string;
  level1TimeMs: number;
  level2TimeMs: number;
  level3TimeMs: number;
  level4TimeMs: number;
  level5TimeMs: number;
  totalTimeMs: number;
  completedAt: string;
}
