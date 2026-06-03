import { createRequire } from 'node:module';
import { PNG } from 'pngjs';
import { ARENA_OBJECTS } from '../shared/arena-objects.js';

const require = createRequire(import.meta.url);

const ARENA_WORLD = 400;
const HALF_ARENA = ARENA_WORLD / 2;

interface GLContext {
  RGBA: number;
  UNSIGNED_BYTE: number;
  readPixels(x: number, y: number, width: number, height: number, format: number, type: number, pixels: Uint8Array): void;
}

const RETICLE_COLOR: [number, number, number, number] = [0xff, 0x52, 0x52, 255];

function setPixel(
  buffer: Uint8Array,
  width: number,
  height: number,
  x: number,
  y: number,
  color: [number, number, number, number],
): void {
  if (x < 0 || x >= width || y < 0 || y >= height) {
    return;
  }

  const idx = (y * width + x) * 4;
  buffer[idx] = color[0];
  buffer[idx + 1] = color[1];
  buffer[idx + 2] = color[2];
  buffer[idx + 3] = color[3];
}

function drawReticle(buffer: Uint8Array, width: number, height: number): void {
  const centerX = Math.floor(width / 2);
  const centerY = Math.floor(height / 2);
  const armLength = 12;
  const color: [number, number, number, number] = [0xff, 0x52, 0x52, 180];

  for (let dx = -armLength; dx <= armLength; dx++) {
    setPixel(buffer, width, height, centerX + dx, centerY, color);
  }
  for (let dy = -armLength; dy <= armLength; dy++) {
    setPixel(buffer, width, height, centerX, centerY + dy, color);
  }
}

function encodePngFromBuffer(width: number, height: number, buffer: Uint8Array): string {
  const png = new PNG({ width, height });
  png.data.set(buffer);
  return PNG.sync.write(png).toString('base64');
}

function encodePng(
  width: number,
  height: number,
  pixelCallback: (x: number, y: number) => [number, number, number, number],
): string {
  const pixels = new Uint8Array(width * height * 4);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = (y * width + x) * 4;
      const [r, g, b, a] = pixelCallback(x, y);
      pixels[idx] = r;
      pixels[idx + 1] = g;
      pixels[idx + 2] = b;
      pixels[idx + 3] = a;
    }
  }
  drawReticle(pixels, width, height);
  return encodePngFromBuffer(width, height, pixels);
}

function hexToRgba(hex: string): [number, number, number, number] {
  const normalized = hex.replace('#', '');
  const value = normalized.length === 3
    ? normalized
        .split('')
        .map((char) => char + char)
        .join('')
    : normalized;
  const intValue = Number.parseInt(value, 16);
  return [(intValue >> 16) & 0xff, (intValue >> 8) & 0xff, intValue & 0xff, 255];
}

function render2DScene(
  width: number,
  height: number,
  robotX: number,
  robotZ: number,
  robotRotationDeg: number,
): string {
  const scale = width / ARENA_WORLD;
  const bgColor: [number, number, number, number] = [0x22, 0x8b, 0x22, 255];
  const wallColor: [number, number, number, number] = [0x8b, 0x45, 0x13, 255];
  const robotColor: [number, number, number, number] = [0x34, 0x98, 0xdb, 255];
  const dirColor: [number, number, number, number] = [0xff, 0x00, 0x00, 255];

  const wallThicknessWorld = 8;
  const wallThicknessHalfWorld = wallThicknessWorld / 2;

  return encodePng(width, height, (px, py) => {
    const wx = px / scale - HALF_ARENA;
    const wz = HALF_ARENA - py / scale;

    if (
      wx < -HALF_ARENA + wallThicknessHalfWorld ||
      wx > HALF_ARENA - wallThicknessHalfWorld ||
      wz < -HALF_ARENA + wallThicknessHalfWorld ||
      wz > HALF_ARENA - wallThicknessHalfWorld
    ) {
      return wallColor;
    }

    for (const obj of ARENA_OBJECTS) {
      if (obj.type === 'cube') {
        const s = obj.size as { width: number; depth: number };
        if (
          wx >= obj.x - s.width / 2 &&
          wx <= obj.x + s.width / 2 &&
          wz >= obj.z - s.depth / 2 &&
          wz <= obj.z + s.depth / 2
        ) {
          return hexToRgba(obj.color);
        }
      } else {
        const radius = 'radius' in obj.size ? obj.size.radius : 10;
        const dxObj = wx - obj.x;
        const dzObj = wz - obj.z;
        if (dxObj * dxObj + dzObj * dzObj <= radius * radius) {
          return hexToRgba(obj.color);
        }
      }
    }

    const dx = wx - robotX;
    const dz = wz - robotZ;
    const rad = (robotRotationDeg * Math.PI) / 180;
    const cosR = Math.cos(-rad);
    const sinR = Math.sin(-rad);
    const rx = dx * cosR - dz * sinR;
    const rz = dx * sinR + dz * cosR;

    const robotW = 14;
    const robotH = 22;
    if (Math.abs(rx) < robotW && Math.abs(rz) < robotH) {
      if (rz > robotH - 8 && Math.abs(rx) < 3) {
        return dirColor;
      }
      return robotColor;
    }

    return bgColor;
  });
}

export class HeadlessSceneRenderer {
  renderMethod: 'webgl' | '2d' | 'none' = 'none';
  private width: number;
  private height: number;
  private glCtx: GLContext | null = null;
  private threeRenderer: unknown = null;
  private scene: unknown = null;
  private camera: unknown = null;
  private robotGroup: unknown = null;
  private THREE: { WebGLRenderer: new (...args: unknown[]) => unknown; Scene: new () => unknown; PerspectiveCamera: new (...args: unknown[]) => unknown; Color: new (c: number) => unknown; AmbientLight: new (...args: unknown[]) => unknown; DirectionalLight: new (...args: unknown[]) => unknown; HemisphereLight: new (...args: unknown[]) => unknown; Mesh: new (...args: unknown[]) => unknown; PlaneGeometry: new (...args: unknown[]) => unknown; BoxGeometry: new (...args: unknown[]) => unknown; SphereGeometry: new (...args: unknown[]) => unknown; ConeGeometry: new (...args: unknown[]) => unknown; MeshLambertMaterial: new (...args: unknown[]) => unknown; MeshStandardMaterial: new (...args: unknown[]) => unknown; Group: new () => unknown } | null = null;

  readonly available: boolean;

  constructor(width = 640, height = 480) {
    this.width = width;
    this.height = height;
    this.available = false;

    let createGL: ((w: number, h: number, opts?: Record<string, unknown>) => unknown) | null = null;
    try {
      createGL = require('gl') as (w: number, h: number, opts?: Record<string, unknown>) => unknown;
    } catch (e) {
      console.error('gl (headless-webgl) not available:', e instanceof Error ? e.message : e);
    }

    let THREE: typeof import('three') | null = null;
    try {
      THREE = require('three') as typeof import('three');
    } catch (e) {
      console.error('three not available:', e instanceof Error ? e.message : e);
    }

    if (createGL && THREE) {
      try {
        const gl = createGL(width, height, {
          preserveDrawingBuffer: true,
          antialias: true,
          alpha: false,
        }) as GLContext;

        const fakeCanvas = {
          width,
          height,
          getContext: () => gl,
          style: {},
          addEventListener: () => {},
          removeEventListener: () => {},
          getBoundingClientRect: () => ({
            left: 0, top: 0, right: width, bottom: height, width, height, x: 0, y: 0, toJSON: () => ({}),
          }),
          clientWidth: width,
          clientHeight: height,
        };

        const renderer = new THREE.WebGLRenderer({
          canvas: fakeCanvas as never,
          antialias: true,
          alpha: false,
        });
        renderer.setSize(width, height);
        renderer.setPixelRatio(1);
        renderer.shadowMap.enabled = true;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87ceeb);
        scene.add(new THREE.AmbientLight(0xffffff, 0.6));

        const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
        dirLight.position.set(100, 200, 100);
        dirLight.castShadow = true;
        scene.add(dirLight);
        scene.add(new THREE.HemisphereLight(0x87ceeb, 0x228b22, 0.6));

        const ground = new THREE.Mesh(
          new THREE.PlaneGeometry(400, 400),
          new THREE.MeshLambertMaterial({ color: 0x90ee90 }),
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        const wallMat = new THREE.MeshStandardMaterial({ color: 0x8b4513, roughness: 0.85, metalness: 0.1 });
        const wallDefs = [
          { w: 408, d: 8, x: 0, z: 204 },
          { w: 408, d: 8, x: 0, z: -204 },
          { w: 8, d: 400, x: 204, z: 0 },
          { w: 8, d: 400, x: -204, z: 0 },
        ];
        for (const def of wallDefs) {
          const wall = new THREE.Mesh(new THREE.BoxGeometry(def.w, 15, def.d), wallMat);
          wall.position.set(def.x, 7.5, def.z);
          wall.castShadow = true;
          wall.receiveShadow = true;
          scene.add(wall);
        }

        for (const obj of ARENA_OBJECTS) {
          let geometry: { type?: string } | null = null;
          if (obj.type === 'cube') {
            const s = obj.size as { width: number; height: number; depth: number };
            geometry = new THREE.BoxGeometry(s.width, s.height, s.depth);
          } else if (obj.type === 'sphere') {
            const s = obj.size as { radius: number };
            geometry = new THREE.SphereGeometry(s.radius, 32, 32);
          } else {
            const s = obj.size as { radius: number; height: number };
            geometry = new THREE.ConeGeometry(s.radius, s.height, 32);
          }
          const material = new THREE.MeshStandardMaterial({ color: obj.color, roughness: 0.7, metalness: 0.1 });
          const mesh = new THREE.Mesh(geometry as never, material);
          const yPos = obj.type === 'sphere'
            ? (obj.size as { radius: number }).radius
            : obj.type === 'cone'
              ? (obj.size as { radius: number; height: number }).height / 2
              : (obj.size as { width: number; height: number; depth: number }).height / 2;
          mesh.position.set(obj.x, yPos, obj.z);
          mesh.castShadow = true;
          mesh.receiveShadow = true;
          scene.add(mesh);
        }

        const robot = new THREE.Group();
        robot.add(new THREE.Mesh(
          new THREE.BoxGeometry(20, 4, 30),
          new THREE.MeshStandardMaterial({ color: 0x3498db }),
        ));
        scene.add(robot);

        const camera = new THREE.PerspectiveCamera(100, width / height, 0.1, 1500);

        this.glCtx = gl;
        this.threeRenderer = renderer;
        this.scene = scene;
        this.camera = camera;
        this.robotGroup = robot;
        this.THREE = {
          WebGLRenderer: THREE.WebGLRenderer,
          Scene: THREE.Scene,
          PerspectiveCamera: THREE.PerspectiveCamera,
          Color: THREE.Color,
          AmbientLight: THREE.AmbientLight,
          DirectionalLight: THREE.DirectionalLight,
          HemisphereLight: THREE.HemisphereLight,
          Mesh: THREE.Mesh,
          PlaneGeometry: THREE.PlaneGeometry,
          BoxGeometry: THREE.BoxGeometry,
          SphereGeometry: THREE.SphereGeometry,
          ConeGeometry: THREE.ConeGeometry,
          MeshLambertMaterial: THREE.MeshLambertMaterial,
          MeshStandardMaterial: THREE.MeshStandardMaterial,
          Group: THREE.Group,
        } as unknown as HeadlessSceneRenderer['THREE'];
        this.renderMethod = 'webgl';
        this.available = true;
        return;
      } catch (e) {
        console.error('WebGL initialization failed, falling back to 2D renderer:', e instanceof Error ? e.message : e);
        // WebGL initialization failed
      }
    }

    this.renderMethod = '2d';
    this.available = true;
  }

  render(robotX: number, robotZ: number, robotRotationDeg: number): string {
    if (!this.available) {
      throw new Error('Renderizador nao inicializado.');
    }

    if (this.renderMethod === '2d') {
      return render2DScene(this.width, this.height, robotX, robotZ, robotRotationDeg);
    }

    if (!this.glCtx || !this.threeRenderer || !this.scene || !this.camera || !this.robotGroup || !this.THREE) {
      throw new Error('Renderizador nao inicializado.');
    }

    const renderer = this.threeRenderer as { render: (s: unknown, c: unknown) => void };
    const scene = this.scene as { background: unknown };
    const camera = this.camera as {
      position: { set: (x: number, y: number, z: number) => void };
      lookAt: (x: number, y: number, z: number) => void };
    const robot = this.robotGroup as { position: { set: (x: number, y: number, z: number) => void }; rotation: { y: number } };

    const rad = (robotRotationDeg * Math.PI) / 180;
    const frontX = Math.sin(rad);
    const frontZ = Math.cos(rad);

    robot.position.set(robotX, 0, robotZ);
    robot.rotation.y = rad;

    const wasVisible = ((robot as unknown) as { visible: boolean }).visible;
    ((robot as unknown) as { visible: boolean }).visible = false;

    const camHeight = 3;
    const camForward = 12;
    camera.position.set(
      robotX + frontX * camForward,
      camHeight,
      robotZ + frontZ * camForward,
    );
    camera.lookAt(
      robotX + frontX * 200,
      camHeight,
      robotZ + frontZ * 200,
    );

    renderer.render(scene, camera);

    ((robot as unknown) as { visible: boolean }).visible = wasVisible;

    const pixels = new Uint8Array(this.width * this.height * 4);
    this.glCtx.readPixels(
      0, 0, this.width, this.height,
      this.glCtx.RGBA, this.glCtx.UNSIGNED_BYTE, pixels,
    );

    const png = new PNG({ width: this.width, height: this.height });
    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        const srcIdx = ((this.height - 1 - y) * this.width + x) * 4;
        const dstIdx = (y * this.width + x) * 4;
        png.data[dstIdx] = pixels[srcIdx];
        png.data[dstIdx + 1] = pixels[srcIdx + 1];
        png.data[dstIdx + 2] = pixels[srcIdx + 2];
        png.data[dstIdx + 3] = 255;
      }
    }

    drawReticle(png.data, this.width, this.height);

    return PNG.sync.write(png).toString('base64');
  }

  dispose(): void {
    const r = this.threeRenderer as { dispose?: () => void } | null;
    if (r?.dispose) {
      r.dispose();
    }
  }
}
