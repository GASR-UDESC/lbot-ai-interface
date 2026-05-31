import { Injectable } from '@angular/core';
import { LevelConfig, LEVEL_CONFIGS } from '../models/level-config.model';

/**
 * Service providing read-only access to the game's level configurations.
 * Level data is statically defined in level-config.model.ts (no HTTP calls needed).
 */
@Injectable({
  providedIn: 'root'
})
export class LevelConfigService {

  /**
   * Returns the LevelConfig for the given id (1-based).
   * Throws if the id does not match any defined level.
   */
  getLevel(id: number): LevelConfig {
    const config = LEVEL_CONFIGS.find(l => l.id === id);
    if (!config) {
      throw new Error(`[LevelConfigService] Level with id "${id}" not found.`);
    }
    return config;
  }

  /** Returns all level configurations in order. */
  getAllLevels(): LevelConfig[] {
    return LEVEL_CONFIGS;
  }

  /** Returns the total number of levels in the game. */
  getTotalLevels(): number {
    return LEVEL_CONFIGS.length;
  }
}
