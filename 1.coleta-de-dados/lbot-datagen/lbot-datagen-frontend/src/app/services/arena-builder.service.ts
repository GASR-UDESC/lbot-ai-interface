import { Injectable } from '@angular/core';
import * as THREE from 'three';
import * as CANNON from 'cannon-es';
import { LevelConfig, ThemeConfig } from '../models/level-config.model';
import { ObstacleMeshFactory } from './obstacle-mesh.factory';

export interface ObstacleData {
  mesh: THREE.Mesh | THREE.Group;
  body: CANNON.Body;
}

@Injectable({
  providedIn: 'root'
})
export class ArenaBuilderService {
  constructor(private meshFactory: ObstacleMeshFactory) {}

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
    const wallHeight = 15;
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
   * Creates obstacles (walls, ramps, crates) in the arena using composite meshes.
   */
  createObstacles(scene: THREE.Scene, world: CANNON.World): ObstacleData[] {
    const obstacles: ObstacleData[] = [];
    const defaultColor = '#D2691E';

    // Maze walls (using factory wall with pillars)
    const mazeWalls = [
      { x: -100, z: 80, width: 6, height: 18, depth: 100 },
      { x: 100, z: 80, width: 6, height: 18, depth: 100 },
      { x: -100, z: -80, width: 6, height: 18, depth: 100 },
      { x: 100, z: -80, width: 6, height: 18, depth: 100 },
      { x: 0, z: 100, width: 80, height: 18, depth: 6 },
      { x: 0, z: -100, width: 80, height: 18, depth: 6 },
    ];

    mazeWalls.forEach((wall, index) => {
      const mesh = this.meshFactory.createWallWithPillars(wall.width, wall.height, wall.depth, defaultColor, index);
      mesh.position.set(wall.x, 0, wall.z);
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

    // Ramps (using factory ramp)
    const ramps = [
      { x: -110, z: 130, width: 40, height: 3, depth: 50, rotation: 0, angle: Math.PI / 8 },
      { x: 110, z: 130, width: 40, height: 3, depth: 50, rotation: 0, angle: Math.PI / 8 },
      { x: -110, z: -130, width: 40, height: 3, depth: 50, rotation: 0, angle: Math.PI / 9 },
      { x: 110, z: -130, width: 40, height: 3, depth: 50, rotation: 0, angle: Math.PI / 9 },
    ];

    ramps.forEach(ramp => {
      const mesh = this.meshFactory.createRamp(ramp.width, ramp.height, ramp.depth, '#DEB887', 0);
      const yOffset = Math.sin(ramp.angle) * ramp.depth / 4;
      mesh.position.set(ramp.x, yOffset, ramp.z);
      mesh.rotation.y = ramp.rotation;
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

    // Crates (using factory crate stack)
    const crates = [
      { x: -130, z: 0, size: 15 },
      { x: 130, z: 0, size: 15 },
      { x: 0, z: 50, size: 12 },
      { x: 0, z: -50, size: 12 },
    ];

    crates.forEach((crate, index) => {
      const mesh = this.meshFactory.createCrateStack(crate.size, crate.size, crate.size, defaultColor, index);
      mesh.position.set(crate.x, 0, crate.z);
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
      limit: 190,
      size: 400,
      wallHeight: 15,
      wallThickness: 8
    };
  }

  // ─── CanvasTexture helpers for ground ─────────────────────────────────

  private createCanvasTexture(width: number, height: number, drawFn: (ctx: CanvasRenderingContext2D) => void): THREE.CanvasTexture {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d')!;
    drawFn(ctx);
    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(100, 100);
    return texture;
  }

  createGrassTexture(): THREE.CanvasTexture {
    return this.createCanvasTexture(256, 256, (ctx) => {
      ctx.fillStyle = '#228B22';
      ctx.fillRect(0, 0, 256, 256);
      for (let i = 0; i < 200; i++) {
        const x = Math.random() * 256;
        const y = Math.random() * 256;
        const len = 5 + Math.random() * 10;
        ctx.strokeStyle = Math.random() > 0.5 ? '#32CD32' : '#90EE90';
        ctx.lineWidth = 1 + Math.random() * 2;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + (Math.random() - 0.5) * 4, y - len);
        ctx.stroke();
      }
      for (let i = 0; i < 50; i++) {
        ctx.fillStyle = '#90EE90';
        ctx.beginPath();
        ctx.arc(Math.random() * 256, Math.random() * 256, 1 + Math.random() * 2, 0, Math.PI * 2);
        ctx.fill();
      }
    });
  }

  createConcreteTexture(): THREE.CanvasTexture {
    return this.createCanvasTexture(256, 256, (ctx) => {
      ctx.fillStyle = '#D3D3D3';
      ctx.fillRect(0, 0, 256, 256);
      for (let i = 0; i < 30; i++) {
        ctx.fillStyle = `rgba(100, 100, 100, ${0.1 + Math.random() * 0.2})`;
        ctx.beginPath();
        ctx.arc(Math.random() * 256, Math.random() * 256, 5 + Math.random() * 15, 0, Math.PI * 2);
        ctx.fill();
      }
      for (let i = 0; i < 8; i++) {
        ctx.strokeStyle = `rgba(80, 80, 80, ${0.2 + Math.random() * 0.3})`;
        ctx.lineWidth = 1 + Math.random() * 2;
        ctx.beginPath();
        ctx.moveTo(Math.random() * 256, Math.random() * 256);
        ctx.lineTo(Math.random() * 256, Math.random() * 256);
        ctx.stroke();
      }
    });
  }

  createAsphaltTexture(): THREE.CanvasTexture {
    return this.createCanvasTexture(256, 256, (ctx) => {
      ctx.fillStyle = '#696969';
      ctx.fillRect(0, 0, 256, 256);
      for (let i = 0; i < 400; i++) {
        ctx.fillStyle = Math.random() > 0.5 ? '#808080' : '#A9A9A9';
        ctx.beginPath();
        ctx.arc(Math.random() * 256, Math.random() * 256, 0.5 + Math.random() * 2, 0, Math.PI * 2);
        ctx.fill();
      }
    });
  }

  createDirtTexture(): THREE.CanvasTexture {
    return this.createCanvasTexture(256, 256, (ctx) => {
      ctx.fillStyle = '#8B4513';
      ctx.fillRect(0, 0, 256, 256);
      for (let i = 0; i < 100; i++) {
        ctx.fillStyle = Math.random() > 0.5 ? '#A0522D' : '#CD853F';
        ctx.beginPath();
        ctx.arc(Math.random() * 256, Math.random() * 256, 2 + Math.random() * 8, 0, Math.PI * 2);
        ctx.fill();
      }
    });
  }

  createIndustrialTexture(): THREE.CanvasTexture {
    return this.createCanvasTexture(256, 256, (ctx) => {
      ctx.fillStyle = '#4A4A4A';
      ctx.fillRect(0, 0, 256, 256);
      // Grid lines
      ctx.strokeStyle = '#666666';
      ctx.lineWidth = 2;
      for (let i = 0; i <= 256; i += 32) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, 256);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(256, i);
        ctx.stroke();
      }
      // Rivet dots
      ctx.fillStyle = '#888888';
      for (let x = 16; x < 256; x += 32) {
        for (let y = 16; y < 256; y += 32) {
          ctx.beginPath();
          ctx.arc(x, y, 3, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    });
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

    for (const obsCfg of config.obstacles) {
      const rampAngle = obsCfg.rampAngle ?? 0;
      const yOffset = obsCfg.type === 'ramp'
        ? Math.sin(rampAngle) * obsCfg.depth / 4
        : 0;

      // Use factory for visual mesh (composite)
      const mesh = this.meshFactory.createMesh(
        obsCfg.type as any,
        obsCfg.width,
        obsCfg.height,
        obsCfg.depth,
        config.theme.obstacleColor,
        obsCfg.rotationY
      );

      mesh.position.set(obsCfg.x, yOffset, obsCfg.z);
      if (obsCfg.rotationY !== undefined) {
        mesh.rotation.y = obsCfg.rotationY * Math.PI / 180;
      }
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);

      // Physics body (simple box approximation)
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
   * Selects a CanvasTexture based on the theme's groundColor.
   */
  private createGroundTexture(theme: ThemeConfig): THREE.CanvasTexture {
    const gc = theme.groundColor.toLowerCase();
    // Map known palette colors to textures
    if (gc === '#7c9a5e' || gc === '#228b22') {
      return this.createGrassTexture();
    }
    if (gc === '#d3d3d3') {
      return this.createConcreteTexture();
    }
    if (gc === '#696969') {
      return this.createAsphaltTexture();
    }
    if (gc === '#8b4513') {
      return this.createDirtTexture();
    }
    if (gc === '#2f4f4f') {
      return this.createIndustrialTexture();
    }
    // Fallback: infer by hue
    if (gc.includes('2') || gc.includes('4')) {
      return this.createIndustrialTexture();
    }
    return this.createGrassTexture();
  }

  /**
   * Creates a themed ground plane using the level theme's groundColor + CanvasTexture.
   * Returns the mesh; caller must add it to the scene.
   */
  createThemedGround(theme: ThemeConfig): THREE.Mesh {
    const colorHex = parseInt(theme.groundColor.replace('#', ''), 16);
    const texture = this.createGroundTexture(theme);
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(800, 800),
      new THREE.MeshLambertMaterial({ map: texture, color: colorHex })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    return ground;
  }

  /**
   * Creates arena boundary walls using the level theme's wallColor.
   * Returns the meshes; caller must add them to the scene.
   * Adds thematic details based on the ground color.
   */
  createThemedWalls(scene: THREE.Scene, theme: ThemeConfig): THREE.Mesh[] {
    const colorHex = parseInt(theme.wallColor.replace('#', ''), 16);
    const material = new THREE.MeshStandardMaterial({
      color: colorHex,
      roughness: 0.85,
      metalness: 0.1
    });

    const wallHeight = 15;
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

    const walls: THREE.Mesh[] = [];

    wallDefs.forEach(def => {
      const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(def.w, def.h, def.d),
        material
      );
      mesh.position.set(def.x, def.y, def.z);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      walls.push(mesh);
    });

    // Add thematic details based on ground color
    const gc = theme.groundColor.toLowerCase();
    if (gc === '#7c9a5e' || gc === '#8b4513') {
      // Campo / Armazem: wooden planks (same as createArenaWalls)
      const plankMat = new THREE.MeshStandardMaterial({ color: 0x654321, roughness: 0.9 });
      const plankCount = Math.floor(wallHeight / 3);
      wallDefs.forEach((def, idx) => {
        const wall = walls[idx];
        const isHorizontal = def.d > def.w;
        for (let i = 0; i < plankCount; i++) {
          const plank = new THREE.Mesh(
            new THREE.BoxGeometry(
              isHorizontal ? def.w * 0.98 : def.w + 0.5,
              0.5,
              isHorizontal ? def.d + 0.5 : def.d * 0.98
            ),
            plankMat
          );
          plank.position.set(
            wall.position.x,
            wall.position.y - wallHeight / 2 + i * 3 + 1.5,
            wall.position.z
          );
          plank.rotation.y = wall.rotation.y;
          scene.add(plank);
        }
      });
    } else if (gc === '#d3d3d3') {
      // Escritorio: concrete panels with lines
      const lineMat = new THREE.MeshStandardMaterial({ color: 0x555555, roughness: 0.9 });
      wallDefs.forEach((def, idx) => {
        const wall = walls[idx];
        const isHorizontal = def.d > def.w;
        const segments = 4;
        const segmentSize = isHorizontal ? def.w / segments : def.d / segments;
        for (let i = 1; i < segments; i++) {
          const line = new THREE.Mesh(
            new THREE.BoxGeometry(
              isHorizontal ? 0.5 : def.w + 0.5,
              wallHeight * 0.95,
              isHorizontal ? def.d + 0.5 : 0.5
            ),
            lineMat
          );
          const offset = -((isHorizontal ? def.w : def.d) / 2) + i * segmentSize;
          line.position.set(
            isHorizontal ? wall.position.x + offset : wall.position.x,
            wall.position.y,
            isHorizontal ? wall.position.z : wall.position.z + offset
          );
          scene.add(line);
        }
      });
    } else if (gc === '#696969') {
      // Cidade: concrete barrier with stripes
      const stripeMat = new THREE.MeshStandardMaterial({ color: 0xFFFF00, roughness: 0.7 });
      wallDefs.forEach((def, idx) => {
        const wall = walls[idx];
        const isHorizontal = def.d > def.w;
        const stripeCount = 6;
        const stripeSize = isHorizontal ? def.w / stripeCount : def.d / stripeCount;
        for (let i = 0; i < stripeCount; i += 2) {
          const stripe = new THREE.Mesh(
            new THREE.BoxGeometry(
              isHorizontal ? stripeSize * 0.8 : def.w + 1,
              wallHeight * 0.2,
              isHorizontal ? def.d + 1 : stripeSize * 0.8
            ),
            stripeMat
          );
          const offset = -((isHorizontal ? def.w : def.d) / 2) + i * stripeSize + stripeSize / 2;
          stripe.position.set(
            isHorizontal ? wall.position.x + offset : wall.position.x,
            wall.position.y + wallHeight * 0.3,
            isHorizontal ? wall.position.z : wall.position.z + offset
          );
          scene.add(stripe);
        }
      });
    } else if (gc === '#228b22') {
      // Floresta: tree trunks (vertical cylinders)
      const trunkMat = new THREE.MeshStandardMaterial({ color: 0x8B4513, roughness: 0.9 });
      wallDefs.forEach((def, idx) => {
        const wall = walls[idx];
        const isHorizontal = def.d > def.w;
        const trunkCount = 4;
        const spacing = isHorizontal ? def.w / (trunkCount + 1) : def.d / (trunkCount + 1);
        for (let i = 1; i <= trunkCount; i++) {
          const trunk = new THREE.Mesh(
            new THREE.CylinderGeometry(2, 2, wallHeight + 2, 8),
            trunkMat
          );
          const offset = -((isHorizontal ? def.w : def.d) / 2) + i * spacing;
          trunk.position.set(
            isHorizontal ? wall.position.x + offset : wall.position.x,
            wall.position.y,
            isHorizontal ? wall.position.z : wall.position.z + offset
          );
          scene.add(trunk);
        }
      });
    } else if (gc === '#2f4f4f') {
      // Industrial: metal with rivets (small spheres)
      const rivetMat = new THREE.MeshStandardMaterial({ color: 0x888888, roughness: 0.5, metalness: 0.8 });
      wallDefs.forEach((def, idx) => {
        const wall = walls[idx];
        const isHorizontal = def.d > def.w;
        const rivetRows = 2;
        const rivetCols = 6;
        const rowSpacing = wallHeight / (rivetRows + 1);
        const colSpacing = isHorizontal ? def.w / (rivetCols + 1) : def.d / (rivetCols + 1);
        for (let r = 1; r <= rivetRows; r++) {
          for (let c = 1; c <= rivetCols; c++) {
            const rivet = new THREE.Mesh(
              new THREE.SphereGeometry(1, 6, 4),
              rivetMat
            );
            const colOffset = -((isHorizontal ? def.w : def.d) / 2) + c * colSpacing;
            rivet.position.set(
              isHorizontal ? wall.position.x + colOffset : wall.position.x + (wallThickness / 2 + 1),
              wall.position.y - wallHeight / 2 + r * rowSpacing,
              isHorizontal ? wall.position.z + (wallThickness / 2 + 1) : wall.position.z + colOffset
            );
            scene.add(rivet);
          }
        }
      });
    }

    return walls;
  }
}
