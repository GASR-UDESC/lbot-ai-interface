import { Injectable } from '@angular/core';
import { LevelConfig, ObstacleConfig } from '../models/level-config.model';

export interface Point {
  x: number;
  z: number;
}

export interface ValidationResult {
  completable: boolean;
  estimatedCommands: number;
  path: Point[];
}

interface GridCell {
  x: number;
  z: number;
  blocked: boolean;
}

interface AStarNode {
  x: number;
  z: number;
  g: number;
  h: number;
  f: number;
  parent: AStarNode | null;
}

@Injectable({
  providedIn: 'root'
})
export class LevelValidatorService {
  private readonly CELL_SIZE = 20;
  private readonly GRID_HALF = 10; // 20x20 grid for 400x400 arena
  private readonly ROBOT_RADIUS = 20; // Safety margin for robot size

  /**
   * Validates a level by checking if there is a path from start to goal
   * using A* pathfinding on a grid.
   */
  validateLevel(config: LevelConfig): ValidationResult {
    const grid = this.buildGrid(config);
    const start = this.worldToGrid(config.startPoint.x, config.startPoint.z);
    const goal = this.worldToGrid(config.goalPoint.x, config.goalPoint.z);

    const path = this.aStar(grid, start, goal);
    const completable = path.length > 0;
    const estimatedCommands = completable ? this.estimateCommands(path) : -1;

    return {
      completable,
      estimatedCommands,
      path
    };
  }

  /**
   * Builds a grid and marks cells blocked by obstacles.
   */
  private buildGrid(config: LevelConfig): GridCell[][] {
    const grid: GridCell[][] = [];
    for (let i = 0; i < this.GRID_HALF * 2; i++) {
      grid[i] = [];
      for (let j = 0; j < this.GRID_HALF * 2; j++) {
        grid[i][j] = {
          x: i,
          z: j,
          blocked: false
        };
      }
    }

    // Mark cells blocked by obstacles
    for (const obs of config.obstacles) {
      const minX = obs.x - obs.width / 2 - this.ROBOT_RADIUS;
      const maxX = obs.x + obs.width / 2 + this.ROBOT_RADIUS;
      const minZ = obs.z - obs.depth / 2 - this.ROBOT_RADIUS;
      const maxZ = obs.z + obs.depth / 2 + this.ROBOT_RADIUS;

      const startCell = this.worldToGrid(minX, minZ);
      const endCell = this.worldToGrid(maxX, maxZ);

      for (let x = Math.max(0, startCell.x); x <= Math.min(this.GRID_HALF * 2 - 1, endCell.x); x++) {
        for (let z = Math.max(0, startCell.z); z <= Math.min(this.GRID_HALF * 2 - 1, endCell.z); z++) {
          grid[x][z].blocked = true;
        }
      }
    }

    // Also mark cells near arena walls as blocked (safety margin)
    const wallMargin = Math.ceil(this.ROBOT_RADIUS / this.CELL_SIZE);
    for (let i = 0; i < wallMargin; i++) {
      for (let j = 0; j < this.GRID_HALF * 2; j++) {
        grid[i][j].blocked = true;
        grid[this.GRID_HALF * 2 - 1 - i][j].blocked = true;
        grid[j][i].blocked = true;
        grid[j][this.GRID_HALF * 2 - 1 - i].blocked = true;
      }
    }

    return grid;
  }

  /**
   * Converts world coordinates to grid coordinates.
   */
  private worldToGrid(worldX: number, worldZ: number): { x: number; z: number } {
    const x = Math.floor((worldX + 200) / this.CELL_SIZE);
    const z = Math.floor((worldZ + 200) / this.CELL_SIZE);
    return {
      x: Math.max(0, Math.min(this.GRID_HALF * 2 - 1, x)),
      z: Math.max(0, Math.min(this.GRID_HALF * 2 - 1, z))
    };
  }

  /**
   * Converts grid coordinates to world coordinates (center of cell).
   */
  private gridToWorld(gridX: number, gridZ: number): Point {
    return {
      x: (gridX + 0.5) * this.CELL_SIZE - 200,
      z: (gridZ + 0.5) * this.CELL_SIZE - 200
    };
  }

  /**
   * A* pathfinding algorithm.
   */
  private aStar(grid: GridCell[][], start: { x: number; z: number }, goal: { x: number; z: number }): Point[] {
    const openSet: AStarNode[] = [];
    const closedSet = new Set<string>();
    const startNode: AStarNode = {
      x: start.x,
      z: start.z,
      g: 0,
      h: this.heuristic(start.x, start.z, goal.x, goal.z),
      f: 0,
      parent: null
    };
    startNode.f = startNode.g + startNode.h;
    openSet.push(startNode);

    const directions = [
      { dx: 1, dz: 0 },
      { dx: -1, dz: 0 },
      { dx: 0, dz: 1 },
      { dx: 0, dz: -1 }
    ];

    while (openSet.length > 0) {
      // Find node with lowest f
      let currentIndex = 0;
      for (let i = 1; i < openSet.length; i++) {
        if (openSet[i].f < openSet[currentIndex].f) {
          currentIndex = i;
        }
      }
      const current = openSet[currentIndex];

      if (current.x === goal.x && current.z === goal.z) {
        // Reconstruct path
        const path: Point[] = [];
        let node: AStarNode | null = current;
        while (node) {
          path.unshift(this.gridToWorld(node.x, node.z));
          node = node.parent;
        }
        return path;
      }

      openSet.splice(currentIndex, 1);
      closedSet.add(`${current.x},${current.z}`);

      for (const dir of directions) {
        const nx = current.x + dir.dx;
        const nz = current.z + dir.dz;

        if (nx < 0 || nx >= this.GRID_HALF * 2 || nz < 0 || nz >= this.GRID_HALF * 2) {
          continue;
        }

        if (grid[nx][nz].blocked || closedSet.has(`${nx},${nz}`)) {
          continue;
        }

        const g = current.g + this.CELL_SIZE;
        const h = this.heuristic(nx, nz, goal.x, goal.z);
        const f = g + h;

        const existingNode = openSet.find(n => n.x === nx && n.z === nz);
        if (existingNode) {
          if (g < existingNode.g) {
            existingNode.g = g;
            existingNode.f = f;
            existingNode.parent = current;
          }
        } else {
          openSet.push({
            x: nx,
            z: nz,
            g,
            h,
            f,
            parent: current
          });
        }
      }
    }

    return []; // No path found
  }

  /**
   * Manhattan distance heuristic.
   */
  private heuristic(x1: number, z1: number, x2: number, z2: number): number {
    return (Math.abs(x1 - x2) + Math.abs(z1 - z2)) * this.CELL_SIZE;
  }

  /**
   * Estimates the number of LBML commands needed for a path.
   * 
   * LBML commands:
   * - D[value]F: move forward by value units
   * - R90L or R90R: rotate 90 degrees left or right
   * 
   * The robot starts facing +Z (0 degrees).
   * Directions on the grid: +Z = 0°, +X = 90°, -Z = 180°, -X = 270°.
   */
  private estimateCommands(path: Point[]): number {
    if (path.length < 2) {
      return 0;
    }

    let commands = 0;
    let currentDir: number | null = null; // 0 = +Z, 90 = +X, 180 = -Z, 270 = -X
    let currentDistance = 0;

    for (let i = 1; i < path.length; i++) {
      const dx = path[i].x - path[i - 1].x;
      const dz = path[i].z - path[i - 1].z;

      let stepDir: number;
      if (dx > 0) stepDir = 90;
      else if (dx < 0) stepDir = 270;
      else if (dz > 0) stepDir = 0;
      else stepDir = 180;

      if (currentDir === null) {
        currentDir = stepDir;
        currentDistance = this.CELL_SIZE;
      } else if (currentDir === stepDir) {
        currentDistance += this.CELL_SIZE;
      } else {
        // Direction changed: emit distance command
        commands++;
        currentDistance = this.CELL_SIZE;

        // Calculate rotation
        const diff = (stepDir - currentDir + 360) % 360;
        if (diff === 90) {
          commands++; // R90R
        } else if (diff === 270) {
          commands++; // R90L
        } else if (diff === 180) {
          commands += 2; // R90L + R90L (or R90R + R90R)
        }

        currentDir = stepDir;
      }
    }

    // Emit final distance command
    if (currentDistance > 0) {
      commands++;
    }

    return commands;
  }
}
