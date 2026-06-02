import * as CANNON from 'cannon-es';
import * as THREE from 'three';
import { formatParsedCommand, parseLbmlSequence, type ParsedCommand } from '../../shared/lbml.js';
import type { SimulatorSnapshot, StatusMessage } from './types.js';

const ROBOT_SPEED = 30;
const ROTATION_SPEED = 90;

export class SimulatorEngine {
  private readonly world: CANNON.World;
  private readonly robotBody: CANNON.Body;
  private readonly robotGroup: THREE.Group;
  private executionToken = 0;
  private readonly state: SimulatorSnapshot = {
    x: 0,
    z: 0,
    rotation: 0,
    isAnimating: false,
    currentCommand: '-',
  };

  constructor(robotGroup: THREE.Group) {
    this.robotGroup = robotGroup;
    this.world = new CANNON.World();
    this.world.gravity.set(0, -9.81, 0);
    this.world.broadphase = new CANNON.NaiveBroadphase();

    const groundShape = new CANNON.Plane();
    const groundBody = new CANNON.Body({ mass: 0 });
    groundBody.addShape(groundShape);
    groundBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
    this.world.addBody(groundBody);

    const robotShape = new CANNON.Box(new CANNON.Vec3(10, 6, 15));
    this.robotBody = new CANNON.Body({ mass: 100 });
    this.robotBody.addShape(robotShape);
    this.robotBody.position.set(0, 6, 0);
    this.robotBody.linearDamping = 0.05;
    this.robotBody.angularDamping = 0.99;
    this.world.addBody(this.robotBody);

    this.syncVisual();
  }

  getSnapshot(): SimulatorSnapshot {
    return { ...this.state };
  }

  step(): void {
    this.world.step(1 / 60);
    this.robotBody.angularVelocity.x = 0;
    this.robotBody.angularVelocity.z = 0;
    this.syncVisual();
    this.updateStateFromBody();
  }

  reset(): void {
    this.executionToken += 1;
    this.robotBody.position.set(0, 6, 0);
    this.robotBody.velocity.set(0, 0, 0);
    this.robotBody.angularVelocity.set(0, 0, 0);
    this.robotBody.quaternion.set(0, 0, 0, 1);
    this.state.rotation = 0;
    this.state.currentCommand = '-';
    this.state.isAnimating = false;
    this.syncVisual();
    this.updateStateFromBody();
  }

  async executeSequence(input: string): Promise<StatusMessage> {
    const parsedCommands = parseLbmlSequence(input);

    if (!parsedCommands) {
      return { kind: 'error', text: 'Comando LBML invalido.' };
    }

    if (parsedCommands.length === 0) {
      return { kind: 'error', text: 'Nenhum comando informado.' };
    }

    if (this.state.isAnimating) {
      return { kind: 'error', text: 'O robo ainda esta executando outro comando.' };
    }

    const runToken = ++this.executionToken;
    this.state.isAnimating = true;

    for (const command of parsedCommands) {
      if (runToken !== this.executionToken) {
        return { kind: 'info', text: 'Sequencia interrompida.' };
      }

      this.state.currentCommand = formatParsedCommand(command);
      const completed = await this.executeCommand(command, runToken);

      if (!completed) {
        return { kind: 'info', text: 'Sequencia interrompida.' };
      }

      await sleep(300);
    }

    if (runToken !== this.executionToken) {
      return { kind: 'info', text: 'Sequencia interrompida.' };
    }

    this.state.isAnimating = false;
    this.state.currentCommand = '-';
    return { kind: 'info', text: 'Sequencia executada com sucesso.' };
  }

  private async executeCommand(command: ParsedCommand, runToken: number): Promise<boolean> {
    if (command.type === 'D') {
      return this.executeDistanceCommand(command, runToken);
    }

    const angle = command.value;
    const targetRotation = this.state.rotation + (command.direction === 'R' ? -angle : angle);
    return this.animateRotation(targetRotation, angle, runToken);
  }

  private async executeDistanceCommand(command: ParsedCommand, runToken: number): Promise<boolean> {
    const distance = command.value;
    let targetX = this.state.x;
    let targetZ = this.state.z;
    const radians = (this.state.rotation * Math.PI) / 180;

    switch (command.direction) {
      case 'F':
        targetX += Math.sin(radians) * distance;
        targetZ += Math.cos(radians) * distance;
        break;
      case 'B':
        targetX -= Math.sin(radians) * distance;
        targetZ -= Math.cos(radians) * distance;
        break;
      case 'L':
        if (!(await this.animateRotation(this.state.rotation + 90, 90, runToken))) {
          return false;
        }
        targetX += Math.sin((this.state.rotation * Math.PI) / 180) * distance;
        targetZ += Math.cos((this.state.rotation * Math.PI) / 180) * distance;
        break;
      case 'R':
        if (!(await this.animateRotation(this.state.rotation - 90, 90, runToken))) {
          return false;
        }
        targetX += Math.sin((this.state.rotation * Math.PI) / 180) * distance;
        targetZ += Math.cos((this.state.rotation * Math.PI) / 180) * distance;
        break;
    }

    return this.animateMovement(targetX, targetZ, distance, runToken);
  }

  private animateMovement(
    targetX: number,
    targetZ: number,
    distance: number,
    runToken: number,
  ): Promise<boolean> {
    return new Promise((resolve) => {
      const startTime = performance.now();
      const duration = (distance / ROBOT_SPEED) * 1000;
      const startPos = this.robotBody.position.clone();
      const targetPos = new CANNON.Vec3(targetX, this.robotBody.position.y, targetZ);

      const animate = () => {
        if (runToken !== this.executionToken) {
          resolve(false);
          return;
        }

        const elapsed = performance.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = progress < 0.5 ? 2 * progress * progress : 1 - Math.pow(-2 * progress + 2, 2) / 2;

        this.robotBody.position.x = startPos.x + (targetPos.x - startPos.x) * eased;
        this.robotBody.position.z = startPos.z + (targetPos.z - startPos.z) * eased;
        this.robotBody.velocity.x = 0;
        this.robotBody.velocity.z = 0;
        this.syncVisual();
        this.updateStateFromBody();

        if (progress < 1) {
          requestAnimationFrame(animate);
          return;
        }

        resolve(true);
      };

      requestAnimationFrame(animate);
    });
  }

  private animateRotation(targetRotation: number, angle: number, runToken: number): Promise<boolean> {
    return new Promise((resolve) => {
      const duration = (Math.abs(angle) / ROTATION_SPEED) * 1000;
      const startTime = performance.now();
      const startRotation = this.state.rotation;

      const animate = () => {
        if (runToken !== this.executionToken) {
          resolve(false);
          return;
        }

        const elapsed = performance.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentRotation = startRotation + (targetRotation - startRotation) * progress;
        const quaternion = new CANNON.Quaternion();
        quaternion.setFromAxisAngle(new CANNON.Vec3(0, 1, 0), (currentRotation * Math.PI) / 180);
        this.robotBody.quaternion.copy(quaternion);
        this.syncVisual();
        this.updateStateFromBody();

        if (progress < 1) {
          requestAnimationFrame(animate);
          return;
        }

        this.state.rotation = targetRotation;
        resolve(true);
      };

      requestAnimationFrame(animate);
    });
  }

  private syncVisual(): void {
    this.robotGroup.position.copy(this.robotBody.position as unknown as THREE.Vector3);
    this.robotGroup.quaternion.copy(this.robotBody.quaternion as unknown as THREE.Quaternion);
  }

  private updateStateFromBody(): void {
    this.state.x = this.robotBody.position.x;
    this.state.z = this.robotBody.position.z;

    const euler = new CANNON.Vec3();
    this.robotBody.quaternion.toEuler(euler);
    this.state.rotation = (euler.y * 180) / Math.PI;
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
