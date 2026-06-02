export type LbmlCommandType = 'D' | 'R';
export type MovementDirection = 'F' | 'B' | 'L' | 'R';
export type RotationDirection = 'L' | 'R';
export type CommandDirection = MovementDirection | RotationDirection;

export interface ParsedCommand {
  type: LbmlCommandType;
  value: number;
  direction: CommandDirection;
}

const COMMAND_REGEX = /^([DR])(\d+)([FBLR]);$/;
const SEQUENCE_REGEX = /^(D\d+[FBLR];|R\d+[LR];)+$/;
const DISTANCE_DIRECTIONS = new Set<MovementDirection>(['F', 'B', 'L', 'R']);
const ROTATION_DIRECTIONS = new Set<RotationDirection>(['L', 'R']);

export function normalizeLbml(input: string): string {
  return input.replace(/\s+/g, '').toUpperCase();
}

export function validateLbml(input: string): boolean {
  const normalized = normalizeLbml(input);
  if (!normalized) {
    return false;
  }

  return SEQUENCE_REGEX.test(normalized);
}

export function parseLbmlCommand(command: string): ParsedCommand | null {
  const normalized = normalizeLbml(command);
  const match = normalized.match(COMMAND_REGEX);

  if (!match) {
    return null;
  }

  const [, type, valueString, direction] = match;
  const value = Number.parseInt(valueString, 10);

  if (type === 'D' && !DISTANCE_DIRECTIONS.has(direction as MovementDirection)) {
    return null;
  }

  if (type === 'R' && !ROTATION_DIRECTIONS.has(direction as RotationDirection)) {
    return null;
  }

  return {
    type: type as LbmlCommandType,
    value,
    direction: direction as CommandDirection,
  };
}

export function parseLbmlSequence(input: string): ParsedCommand[] | null {
  const normalized = normalizeLbml(input);

  if (!normalized) {
    return [];
  }

  if (!validateLbml(normalized)) {
    return null;
  }

  const commands = normalized
    .split(';')
    .filter(Boolean)
    .map((part) => `${part};`)
    .map(parseLbmlCommand);

  if (commands.some((command) => command === null)) {
    return null;
  }

  return commands as ParsedCommand[];
}

export function formatParsedCommand(command: ParsedCommand): string {
  return `${command.type}${command.value}${command.direction}`;
}
