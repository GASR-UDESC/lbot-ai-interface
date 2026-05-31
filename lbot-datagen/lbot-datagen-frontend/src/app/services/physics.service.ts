import { Injectable } from '@angular/core';
import * as CANNON from 'cannon-es';
import * as THREE from 'three';
import { ObstacleData } from './arena-builder.service';
import { ArenaShape } from '../models/level-config.model';

export interface PhysicsSetup {
  world: CANNON.World;
  robotBody: CANNON.Body;
}

@Injectable({
  providedIn: 'root'
})
export class PhysicsService {
  private readonly ARENA_LIMIT = 190;

  // ─── Arena configuration ────────────────────────────────────────────────
  /** Current shape of the arena boundary. */
  private currentArenaShape: ArenaShape = 'square';
  /** Width of the current arena in world units (diameter for circles). */
  private currentArenaWidth = 400;
  /** Height of the current arena in world units (same as width for circles). */
  private currentArenaHeight = 400;
  /** Physics bodies representing the arena boundary walls. Tracked for removal on config change. */
  private arenaWallBodies: CANNON.Body[] = [];

  /**
   * Initializes the physics world
   */
  initWorld(): CANNON.World {
    const world = new CANNON.World();
    world.gravity.set(0, -9.81, 0);
    world.broadphase = new CANNON.NaiveBroadphase();

    this.setupContactMaterials(world);

    return world;
  }

  /**
   * Sets up contact materials for different surface interactions
   */
  private setupContactMaterials(world: CANNON.World): void {
    const defaultMaterial = new CANNON.Material('default');
    const robotMaterial = new CANNON.Material('robot');
    const groundMaterial = new CANNON.Material('ground');

    // Robot-ground contact
    const robotGroundContact = new CANNON.ContactMaterial(
      robotMaterial,
      groundMaterial,
      {
        friction: 0.9,
        restitution: 0.0,
      }
    );

    // Robot-obstacle contact
    const robotObstacleContact = new CANNON.ContactMaterial(
      robotMaterial,
      defaultMaterial,
      {
        friction: 0.8,
        restitution: 0.0,
      }
    );

    world.addContactMaterial(robotGroundContact);
    world.addContactMaterial(robotObstacleContact);
    world.defaultContactMaterial = robotObstacleContact;
  }

  /**
   * Creates physics bodies for static objects (ground, walls).
   * Accepts an optional arena configuration; defaults to a 400×400 square arena.
   */
  createStaticBodies(
    world: CANNON.World,
    arenaShape: ArenaShape = 'square',
    arenaSize: { width: number; height: number } = { width: 400, height: 400 }
  ): void {
    this.currentArenaShape = arenaShape;
    this.currentArenaWidth = arenaSize.width;
    this.currentArenaHeight = arenaSize.height;

    // Ground
    const groundShape = new CANNON.Plane();
    const groundBody = new CANNON.Body({ mass: 0 });
    groundBody.addShape(groundShape);
    groundBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
    groundBody.material = new CANNON.Material('ground');
    world.addBody(groundBody);

    // Arena walls
    this.arenaWallBodies = [];
    this.createArenaWallsBodies(world);
  }

  /**
   * Removes existing arena wall bodies and recreates them with the new configuration.
   * Call this when a level with a different arena shape/size is loaded.
   */
  updateArenaWalls(
    world: CANNON.World,
    arenaShape: ArenaShape,
    arenaSize: { width: number; height: number }
  ): void {
    // Remove old arena wall bodies from the physics world
    for (const body of this.arenaWallBodies) {
      world.removeBody(body);
    }
    this.arenaWallBodies = [];

    // Apply new config
    this.currentArenaShape = arenaShape;
    this.currentArenaWidth = arenaSize.width;
    this.currentArenaHeight = arenaSize.height;

    // Create new wall bodies
    this.createArenaWallsBodies(world);
  }

  /**
   * Creates physics bodies for arena boundary walls using the current internal config.
   * Bodies are tracked in arenaWallBodies for later removal.
   */
  private createArenaWallsBodies(world: CANNON.World): void {
    if (this.currentArenaShape === 'circle') {
      // Circular arena: N=32 Box segments arranged in a polygon approximation
      const N = 32;
      const radius = this.currentArenaWidth / 2;
      const wallHeight = 15;
      const wallThickness = 5;
      const segmentLength = 2 * radius * Math.sin(Math.PI / N);

      for (let i = 0; i < N; i++) {
        const angle = (2 * Math.PI * i) / N;
        const x = radius * Math.cos(angle);
        const z = radius * Math.sin(angle);

        const shape = new CANNON.Box(new CANNON.Vec3(segmentLength / 2, wallHeight / 2, wallThickness / 2));
        const body = new CANNON.Body({ mass: 0 });
        body.addShape(shape);
        body.position.set(x, wallHeight / 2, z);
        // Align segment with tangent at this circle position (same convention as visual mesh)
        body.quaternion.setFromAxisAngle(new CANNON.Vec3(0, 1, 0), Math.PI / 2 + angle);
        world.addBody(body);
        this.arenaWallBodies.push(body);
      }
    } else {
      // Square or rectangle arena: 4 box walls
      const wallThickness = 5;
      const arenaWidth = this.currentArenaWidth;
      const arenaHeight = this.currentArenaHeight;
      const wallHeight = 15;

      const walls = [
        // North
        { x: 0, z:  arenaHeight / 2 + wallThickness / 2, w: (arenaWidth + wallThickness) / 2, d: wallThickness / 2 },
        // South
        { x: 0, z: -arenaHeight / 2 - wallThickness / 2, w: (arenaWidth + wallThickness) / 2, d: wallThickness / 2 },
        // East
        { x:  arenaWidth / 2 + wallThickness / 2, z: 0, w: wallThickness / 2, d: arenaHeight / 2 },
        // West
        { x: -arenaWidth / 2 - wallThickness / 2, z: 0, w: wallThickness / 2, d: arenaHeight / 2 },
      ];

      walls.forEach(wall => {
        const shape = new CANNON.Box(new CANNON.Vec3(wall.w, wallHeight / 2, wall.d));
        const body = new CANNON.Body({ mass: 0 });
        body.addShape(shape);
        body.position.set(wall.x, wallHeight / 2, wall.z);
        world.addBody(body);
        this.arenaWallBodies.push(body);
      });
    }
  }

  /**
   * Creates the robot physics body
   */
  createRobotBody(world: CANNON.World): CANNON.Body {
    const robotShape = new CANNON.Box(new CANNON.Vec3(10, 6, 15));
    const robotBody = new CANNON.Body({ mass: 100 });
    robotBody.addShape(robotShape);
    robotBody.position.set(0, 6, 0);
    robotBody.material = new CANNON.Material('robot');
    robotBody.linearDamping = 0.05;
    robotBody.angularDamping = 0.99;

    robotBody.addEventListener('collide', (e: any) => {
      console.log('Robô colidiu!');
    });

    world.addBody(robotBody);
    return robotBody;
  }

  /**
   * Steps the physics simulation forward
   */
  step(world: CANNON.World, timeStep: number = 1 / 60): void {
    world.step(timeStep);
  }

  /**
   * Stabilizes the robot body (prevents tipping, keeps upright)
   */
  stabilizeRobot(robotBody: CANNON.Body, isAnimating: boolean): void {
    if (isAnimating) return;

    // Force upright orientation
    const upVector = new CANNON.Vec3(0, 1, 0);
    const robotUp = new CANNON.Vec3(0, 1, 0);
    robotBody.quaternion.vmult(robotUp, robotUp);

    const dot = upVector.dot(robotUp);
    if (dot < 0.99) {
      const correctionTorque = upVector.cross(robotUp);
      correctionTorque.scale(200);
      robotBody.applyTorque(correctionTorque);
    }

    // Zero unwanted rotations
    robotBody.angularVelocity.x = 0;
    robotBody.angularVelocity.z = 0;

    // Limit upward velocity (prevent jumping)
    if (robotBody.velocity.y > 0.5) {
      robotBody.velocity.y = 0.5;
    }

    // Accelerate falling if robot is in the air
    if (robotBody.position.y > 7) {
      robotBody.velocity.y -= 2;
    }
  }

  /**
   * Syncs THREE.js object with physics body
   */
  syncVisualWithPhysics(visual: THREE.Group, body: CANNON.Body): void {
    visual.position.copy(body.position as any);
    visual.quaternion.copy(body.quaternion as any);
  }

  /**
   * Checks if a position is valid (no collisions, within arena boundaries).
   *
   * Boundary check is shape-aware:
   *  - square/rectangle: axis-aligned box test using currentArenaWidth/Height
   *  - circle: radial distance test using currentArenaWidth / 2 as radius
   *
   * A 10-unit safety margin is subtracted from each boundary to account for
   * the robot's physical half-width (robotHalfWidth = 10).
   */
  isValidPosition(x: number, z: number, obstacles: ObstacleData[]): boolean {
    // Check arena boundaries
    if (this.currentArenaShape === 'circle') {
      const radius = this.currentArenaWidth / 2 - 10;
      const distFromCenter = Math.sqrt(x * x + z * z);
      if (distFromCenter > radius) {
        return false;
      }
    } else {
      // square or rectangle
      const halfWidth  = this.currentArenaWidth  / 2 - 10;
      const halfHeight = this.currentArenaHeight / 2 - 10;
      if (x < -halfWidth || x > halfWidth || z < -halfHeight || z > halfHeight) {
        return false;
      }
    }

    // Check collision with obstacles
    const testPosition = new CANNON.Vec3(x, 0, z);
    const robotHalfWidth = 10;
    const robotHalfDepth = 15;

    for (const obstacle of obstacles) {
      const obstaclePos = new CANNON.Vec3(obstacle.body.position.x, 0, obstacle.body.position.z);
      const distance = testPosition.distanceTo(obstaclePos);

      let minDistance = 30;

      if (obstacle.body.shapes[0] instanceof CANNON.Box) {
        const boxShape = obstacle.body.shapes[0] as CANNON.Box;
        const obstacleRadius = Math.max(boxShape.halfExtents.x, boxShape.halfExtents.z);
        minDistance = robotHalfWidth + obstacleRadius + 5;
      } else if (obstacle.body.shapes[0] instanceof CANNON.Cylinder) {
        const cylinderShape = obstacle.body.shapes[0] as CANNON.Cylinder;
        minDistance = robotHalfWidth + cylinderShape.radiusTop + 5;
      }

      if (distance < minDistance) {
        console.log(`Colisão detectada! Distância: ${distance.toFixed(1)}, Mínimo: ${minDistance.toFixed(1)}`);
        return false;
      }
    }

    return true;
  }

  /**
   * Finds the maximum valid position along a path
   */
  getMaxValidPosition(
    startX: number,
    startZ: number,
    targetX: number,
    targetZ: number,
    obstacles: ObstacleData[]
  ): { x: number; z: number; blocked: boolean } {
    if (this.isValidPosition(targetX, targetZ, obstacles)) {
      return { x: targetX, z: targetZ, blocked: false };
    }

    console.log(`Movimento bloqueado de (${startX.toFixed(1)}, ${startZ.toFixed(1)}) para (${targetX.toFixed(1)}, ${targetZ.toFixed(1)})`);

    const stepSize = 5;
    const totalDistance = Math.sqrt(Math.pow(targetX - startX, 2) + Math.pow(targetZ - startZ, 2));
    const steps = Math.floor(totalDistance / stepSize);

    if (steps === 0) {
      return { x: startX, z: startZ, blocked: true };
    }

    for (let i = steps; i > 0; i--) {
      const progress = i / steps;
      const testX = startX + (targetX - startX) * progress;
      const testZ = startZ + (targetZ - startZ) * progress;

      if (this.isValidPosition(testX, testZ, obstacles)) {
        return { x: testX, z: testZ, blocked: true };
      }
    }

    return { x: startX, z: startZ, blocked: true };
  }

  /**
   * Finds the maximum valid angular position along a circular arc path.
   *
   * Samples the arc trajectory discretely (stepSize = 5 units) and returns
   * the last valid position before a collision is detected.
   *
   * @param centerX   X coordinate of the arc center
   * @param centerZ   Z coordinate of the arc center
   * @param radius    Radius of the arc
   * @param startAngle  Starting angle on the circle (radians)
   * @param endAngle    Ending angle on the circle (radians, signed)
   * @param obstacles   List of obstacles to check against
   * @returns { angle, x, z, blocked } where angle is the last valid angular
   *          position (radians) and blocked indicates whether a collision was found
   */
  getMaxValidArcPosition(
    centerX: number,
    centerZ: number,
    radius: number,
    startAngle: number,
    endAngle: number,
    obstacles: ObstacleData[]
  ): { angle: number; x: number; z: number; blocked: boolean } {
    const arcSpan = endAngle - startAngle; // signed (negative = clockwise)
    const arcLength = radius * Math.abs(arcSpan);
    const stepSize = 5;
    const steps = Math.max(1, Math.floor(arcLength / stepSize));

    // Iterate from step 1 (step 0 = robot's current position, always valid)
    for (let i = 1; i <= steps; i++) {
      const theta = startAngle + arcSpan * (i / steps);
      const x = centerX + radius * Math.sin(theta);
      const z = centerZ + radius * Math.cos(theta);

      if (!this.isValidPosition(x, z, obstacles)) {
        // Return the last valid position (step i-1)
        const prevTheta = startAngle + arcSpan * ((i - 1) / steps);
        const prevX = centerX + radius * Math.sin(prevTheta);
        const prevZ = centerZ + radius * Math.cos(prevTheta);
        console.log(`Colisão em arco! Step ${i}/${steps}, ângulo válido: ${prevTheta.toFixed(3)} rad`);
        return { angle: prevTheta, x: prevX, z: prevZ, blocked: true };
      }
    }

    // No collision: return the final endpoint
    const finalX = centerX + radius * Math.sin(endAngle);
    const finalZ = centerZ + radius * Math.cos(endAngle);
    return { angle: endAngle, x: finalX, z: finalZ, blocked: false };
  }

  /**
   * Resets robot body to initial position
   */
  resetRobotBody(robotBody: CANNON.Body): void {
    robotBody.position.set(0, 6, 0);
    robotBody.velocity.set(0, 0, 0);
    robotBody.angularVelocity.set(0, 0, 0);
    robotBody.quaternion.set(0, 0, 0, 1);
  }
}
