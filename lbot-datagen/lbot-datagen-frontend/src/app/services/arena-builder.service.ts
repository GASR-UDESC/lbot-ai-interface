import { Injectable } from '@angular/core';
import * as THREE from 'three';
import * as CANNON from 'cannon-es';
import { LevelConfig, ThemeConfig } from '../models/level-config.model';

export interface ObstacleData {
  mesh: THREE.Mesh;
  body: CANNON.Body;
}

@Injectable({
  providedIn: 'root'
})
export class ArenaBuilderService {
  private readonly ARENA_WALL_HEIGHT = 30;


  /**
   * Creates the ground plane
   */
  createGround(): THREE.Mesh {
    // Create grass texture
    const grassTexture = new THREE.TextureLoader().load('data:image/svg+xml;base64,' + btoa(`
      <svg width="64" height="64" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grass" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse">
            <rect width="8" height="8" fill="#228B22"/>
            <path d="M2,8 Q2,6 1,4 Q2,2 3,0" stroke="#32CD32" stroke-width="0.5" fill="none"/>
            <path d="M4,8 Q4,6 5,4 Q4,2 3,0" stroke="#32CD32" stroke-width="0.5" fill="none"/>
            <path d="M6,8 Q6,6 7,4 Q6,2 5,0" stroke="#32CD32" stroke-width="0.5" fill="none"/>
            <circle cx="1" cy="7" r="0.3" fill="#90EE90"/>
            <circle cx="5" cy="6" r="0.2" fill="#90EE90"/>
            <circle cx="7" cy="7" r="0.25" fill="#90EE90"/>
          </pattern>
        </defs>
        <rect width="64" height="64" fill="url(#grass)"/>
      </svg>
    `));
    grassTexture.wrapS = THREE.RepeatWrapping;
    grassTexture.wrapT = THREE.RepeatWrapping;
    grassTexture.repeat.set(100, 100);

    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(800, 800),
      new THREE.MeshLambertMaterial({ map: grassTexture, color: 0x90EE90 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;

    return ground;
  }

  /**
   * Creates a grid helper for the ground
   */
  createGridHelper(): THREE.GridHelper {
    const gridHelper = new THREE.GridHelper(800, 80, 0x4CAF50, 0x90EE90);
    gridHelper.material.opacity = 0.3;
    gridHelper.material.transparent = true;
    return gridHelper;
  }

  /**
   * Creates arena boundary walls
   */
  createArenaWalls(scene: THREE.Scene): THREE.Mesh[] {
    const woodMaterial = new THREE.MeshStandardMaterial({
      color: 0x8B4513,
      roughness: 0.85,
      metalness: 0.1
    });
    const wallHeight = this.ARENA_WALL_HEIGHT;
    const wallThickness = 8;
    const arenaSize = 400;
    const walls: THREE.Mesh[] = [];

    const createWoodenWall = (
      width: number, 
      height: number, 
      depth: number, 
      x: number, 
      y: number, 
      z: number, 
      rotationY = 0
    ): THREE.Mesh => {
      const wall = new THREE.Mesh(
        new THREE.BoxGeometry(width, height, depth),
        woodMaterial
      );
      wall.position.set(x, y, z);
      wall.rotation.y = rotationY;
      wall.castShadow = true;
      wall.receiveShadow = true;

      // Add planks detail
      const plankCount = Math.floor(height / 3);
      for (let i = 0; i < plankCount; i++) {
        const plank = new THREE.Mesh(
          new THREE.BoxGeometry(width * 0.98, 0.5, depth + 0.5),
          new THREE.MeshStandardMaterial({ color: 0x654321, roughness: 0.9 })
        );
        plank.position.set(x, y - height / 2 + i * 3 + 1.5, z);
        plank.rotation.y = rotationY;
        scene.add(plank);
      }

      return wall;
    };

    // North wall
    walls.push(createWoodenWall(
      arenaSize + wallThickness, wallHeight, wallThickness,
      0, wallHeight / 2, arenaSize / 2 + wallThickness / 2
    ));

    // South wall
    walls.push(createWoodenWall(
      arenaSize + wallThickness, wallHeight, wallThickness,
      0, wallHeight / 2, -arenaSize / 2 - wallThickness / 2
    ));

    // East wall
    walls.push(createWoodenWall(
      wallThickness, wallHeight, arenaSize,
      arenaSize / 2 + wallThickness / 2, wallHeight / 2, 0
    ));

    // West wall
    walls.push(createWoodenWall(
      wallThickness, wallHeight, arenaSize,
      -arenaSize / 2 - wallThickness / 2, wallHeight / 2, 0
    ));

    return walls;
  }

  /**
   * Creates obstacles (walls, ramps, crates) in the arena
   */
  createObstacles(scene: THREE.Scene, world: CANNON.World): ObstacleData[] {
    const obstacles: ObstacleData[] = [];

    const woodMaterial = new THREE.MeshStandardMaterial({
      color: 0xD2691E,
      roughness: 0.85,
      metalness: 0.1
    });

    const darkWoodMaterial = new THREE.MeshStandardMaterial({
      color: 0x8B4513,
      roughness: 0.9,
      metalness: 0.05
    });

    const lightWoodMaterial = new THREE.MeshStandardMaterial({
      color: 0xDEB887,
      roughness: 0.8,
      metalness: 0.1
    });

    // Maze walls
    const mazeWalls = [
      { x: -100, z: 80, width: 6, height: 18, depth: 100 },
      { x: 100, z: 80, width: 6, height: 18, depth: 100 },
      { x: -100, z: -80, width: 6, height: 18, depth: 100 },
      { x: 100, z: -80, width: 6, height: 18, depth: 100 },
      { x: 0, z: 100, width: 80, height: 18, depth: 6 },
      { x: 0, z: -100, width: 80, height: 18, depth: 6 },
    ];

    mazeWalls.forEach(wall => {
      const geometry = new THREE.BoxGeometry(wall.width, wall.height, wall.depth);
      const mesh = new THREE.Mesh(geometry, woodMaterial);

      mesh.position.set(wall.x, wall.height / 2, wall.z);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);

      // Physics
      const shape = new CANNON.Box(
        new CANNON.Vec3(wall.width / 2, wall.height / 2, wall.depth / 2)
      );
      const body = new CANNON.Body({ mass: 0 });
      body.addShape(shape);
      body.position.set(wall.x, wall.height / 2, wall.z);
      world.addBody(body);

      obstacles.push({ mesh, body });
    });

    // Ramps
    const ramps = [
      { x: -110, z: 130, width: 40, height: 3, depth: 50, rotation: 0, angle: Math.PI / 8 },
      { x: 110, z: 130, width: 40, height: 3, depth: 50, rotation: 0, angle: Math.PI / 8 },
      { x: -110, z: -130, width: 40, height: 3, depth: 50, rotation: 0, angle: Math.PI / 9 },
      { x: 110, z: -130, width: 40, height: 3, depth: 50, rotation: 0, angle: Math.PI / 9 },
    ];

    ramps.forEach(ramp => {
      const geometry = new THREE.BoxGeometry(ramp.width, ramp.height, ramp.depth);
      const mesh = new THREE.Mesh(geometry, lightWoodMaterial);

      const yOffset = Math.sin(ramp.angle) * ramp.depth / 4;
      mesh.position.set(ramp.x, ramp.height / 2 + yOffset, ramp.z);
      mesh.rotation.y = ramp.rotation;
      mesh.rotation.x = ramp.angle;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);

      // Physics
      const shape = new CANNON.Box(
        new CANNON.Vec3(ramp.width / 2, ramp.height / 2, ramp.depth / 2)
      );
      const body = new CANNON.Body({ mass: 0 });
      body.addShape(shape);
      body.position.set(ramp.x, ramp.height / 2 + yOffset, ramp.z);
      body.quaternion.setFromEuler(ramp.angle, ramp.rotation, 0);
      world.addBody(body);

      obstacles.push({ mesh, body });
    });

    // Crates
    const crates = [
      { x: -130, z: 0, size: 15 },
      { x: 130, z: 0, size: 15 },
      { x: 0, z: 50, size: 12 },
      { x: 0, z: -50, size: 12 },
    ];

    crates.forEach((crate, index) => {
      const geometry = new THREE.BoxGeometry(crate.size, crate.size, crate.size);
      const material = index % 2 === 0 ? darkWoodMaterial : woodMaterial;
      const mesh = new THREE.Mesh(geometry, material);

      mesh.position.set(crate.x, crate.size / 2, crate.z);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);

      // Physics
      const shape = new CANNON.Box(
        new CANNON.Vec3(crate.size / 2, crate.size / 2, crate.size / 2)
      );
      const body = new CANNON.Body({ mass: 0 });
      body.addShape(shape);
      body.position.set(crate.x, crate.size / 2, crate.z);
      world.addBody(body);

      obstacles.push({ mesh, body });
    });

    console.log('[ArenaBuilder] Arena criada com', obstacles.length, 'obstáculos');
    return obstacles;
  }

  /**
   * Gets arena boundaries for collision detection
   */
  getArenaBoundaries() {
    return {
      limit: 185,
      size: 400,
      wallHeight: this.ARENA_WALL_HEIGHT,
      wallThickness: 8
    };
  }

  // ─── Themed / Level-aware methods ───────────────────────────────────────

  /**
   * Creates obstacles based on a LevelConfig, applying the level's theme color.
   * Use this method instead of createObstacles() when running a gamified level.
   */
  createObstaclesFromConfig(
    scene: THREE.Scene,
    world: CANNON.World,
    config: LevelConfig
  ): ObstacleData[] {
    const obstacles: ObstacleData[] = [];

    const colorHex = parseInt(config.theme.obstacleColor.replace('#', ''), 16);
    const material = new THREE.MeshStandardMaterial({
      color: colorHex,
      roughness: 0.85,
      metalness: 0.1
    });

    for (const obsCfg of config.obstacles) {
      const geometry = new THREE.BoxGeometry(obsCfg.width, obsCfg.height, obsCfg.depth);
      const mesh = new THREE.Mesh(geometry, material);

      const rampAngle = obsCfg.rampAngle ?? 0;
      const yOffset = obsCfg.type === 'ramp'
        ? Math.sin(rampAngle) * obsCfg.depth / 4
        : 0;

      mesh.position.set(obsCfg.x, obsCfg.height / 2 + yOffset, obsCfg.z);
      if (obsCfg.type === 'ramp') {
        mesh.rotation.x = rampAngle;
      }
      if (obsCfg.rotationY !== undefined) {
        mesh.rotation.y = obsCfg.rotationY * Math.PI / 180;
      }
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);

      // Physics body
      const shape = new CANNON.Box(
        new CANNON.Vec3(obsCfg.width / 2, obsCfg.height / 2, obsCfg.depth / 2)
      );
      const body = new CANNON.Body({ mass: 0 });
      body.addShape(shape);
      body.position.set(obsCfg.x, obsCfg.height / 2 + yOffset, obsCfg.z);

      if (obsCfg.type === 'ramp' || obsCfg.rotationY !== undefined) {
        const rotY = (obsCfg.rotationY ?? 0) * Math.PI / 180;
        body.quaternion.setFromEuler(rampAngle, rotY, 0);
      }

      world.addBody(body);
      obstacles.push({ mesh, body });
    }

    console.log(`[ArenaBuilder] Level "${config.name}" criado com ${obstacles.length} obstáculos`);
    return obstacles;
  }

  /**
   * Creates a solid-color ground plane using the level theme's groundColor.
   * Returns the mesh; caller must add it to the scene.
   */
  createThemedGround(theme: ThemeConfig): THREE.Mesh {
    const colorHex = parseInt(theme.groundColor.replace('#', ''), 16);
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(800, 800),
      new THREE.MeshLambertMaterial({ color: colorHex })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    return ground;
  }

  /**
   * Creates arena boundary walls using the level theme's wallColor.
   * Returns the meshes; caller must add them to the scene.
   * (scene param reserved for potential sub-element additions in future themes.)
   */
  createThemedWalls(scene: THREE.Scene, theme: ThemeConfig): THREE.Mesh[] {
    // scene param intentionally kept for API consistency with createArenaWalls
    void scene;

    const colorHex = parseInt(theme.wallColor.replace('#', ''), 16);
    const material = new THREE.MeshStandardMaterial({
      color: colorHex,
      roughness: 0.85,
      metalness: 0.1
    });

    const wallHeight = this.ARENA_WALL_HEIGHT;
    const wallThickness = 8;
    const arenaSize = 400;

    const wallDefs = [
      // North
      { w: arenaSize + wallThickness, h: wallHeight, d: wallThickness, x: 0, y: wallHeight / 2, z: arenaSize / 2 + wallThickness / 2 },
      // South
      { w: arenaSize + wallThickness, h: wallHeight, d: wallThickness, x: 0, y: wallHeight / 2, z: -arenaSize / 2 - wallThickness / 2 },
      // East
      { w: wallThickness, h: wallHeight, d: arenaSize, x: arenaSize / 2 + wallThickness / 2, y: wallHeight / 2, z: 0 },
      // West
      { w: wallThickness, h: wallHeight, d: arenaSize, x: -arenaSize / 2 - wallThickness / 2, y: wallHeight / 2, z: 0 },
    ];

    return wallDefs.map(def => {
      const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(def.w, def.h, def.d),
        material
      );
      mesh.position.set(def.x, def.y, def.z);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      return mesh;
    });
  }
}
