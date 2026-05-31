/**
 * Valid command types in LBML.
 */
export type LbmlCommandType = 'D' | 'R' | 'A';

/**
 * Valid directions for movement commands.
 */
export type MovementDirection = 'F' | 'B' | 'L' | 'R';

/**
 * Valid directions for rotation commands.
 */
export type RotationDirection = 'L' | 'R';

/**
 * Union type for all valid directions.
 */
export type CommandDirection = MovementDirection | RotationDirection;

/**
 * Represents a parsed LBML command.
 * 
 * @example
 * // Distance command: move forward 10 units
 * { type: 'D', value: 10, direction: 'F' }
 * 
 * @example
 * // Rotation command: rotate left 90 degrees
 * { type: 'R', value: 90, direction: 'L' }
 */
export interface ParsedCommand {
  /** Command type: 'D' for distance/movement, 'R' for rotation */
  type: LbmlCommandType;
  /** Numeric value: distance in units or angle in degrees */
  value: number;
  /** Direction of the command execution */
  direction: CommandDirection;
}

/**
 * Valid directions for arc commands (which side to curve towards).
 */
export type ArcDirection = 'L' | 'R';

/**
 * Represents a parsed LBML arc command.
 *
 * @example
 * // Arc command: curve right with radius 30 for 90 degrees
 * { type: 'A', radius: 30, direction: 'R', angle: 90 }
 *
 * @example
 * // Arc command: curve left with radius 50 for 180 degrees
 * { type: 'A', radius: 50, direction: 'L', angle: 180 }
 */
export interface ParsedArcCommand {
  /** Command type: always 'A' for arc */
  type: 'A';
  /** Radius of the arc in world units */
  radius: number;
  /** Direction to curve: 'L' for left, 'R' for right */
  direction: ArcDirection;
  /** Total arc angle in degrees */
  angle: number;
}

/**
 * Union type for all parsed LBML commands (distance/rotation or arc).
 */
export type ParsedLbmlCommand = ParsedCommand | ParsedArcCommand;

/**
 * Result of a command execution in the simulator.
 */
export interface CommandExecutionResult {
  /** Whether the command executed successfully */
  success: boolean;
  /** Whether the command was blocked by an obstacle */
  blocked?: boolean;
  /** Error message if command failed */
  error?: string;
}
