import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import type { ServerEvent, SimulatorStateSnapshot } from '../../shared/protocol.js';
import { createArenaWalls, createGridHelper, createGround } from '../simulator/arena.js';
import { createCameraController } from '../simulator/camera.js';
import { createArenaObjects } from '../simulator/objects.js';
import { SimulatorEngine } from '../simulator/engine.js';
import { createRobot } from '../simulator/robot.js';
import { createScene, resizeScene } from '../simulator/scene.js';
import type { SimulatorSnapshot, StatusMessage } from '../simulator/types.js';

const PREVIEW_WIDTH = 400;
const PREVIEW_HEIGHT = 300;
const PREVIEW_THROTTLE_MS = 66;

export interface SimulatorCanvasHandle {
  toggleCamera: () => boolean;
  handleRemoteEvent: (event: ServerEvent) => Promise<StatusMessage | null>;
  getSnapshot: () => SimulatorStateSnapshot;
  bindPreviewCanvas: (canvas: HTMLCanvasElement) => void;
  unbindPreviewCanvas: () => void;
}

interface SimulatorCanvasProps {
  onReady: (handle: SimulatorCanvasHandle) => void;
  onSnapshotChange: (snapshot: SimulatorSnapshot) => void;
}

export function SimulatorCanvas({ onReady, onSnapshotChange }: SimulatorCanvasProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const onReadyRef = useRef(onReady);
  onReadyRef.current = onReady;
  const onSnapshotChangeRef = useRef(onSnapshotChange);
  onSnapshotChangeRef.current = onSnapshotChange;

  const [webglError, setWebglError] = useState<string | null>(null);

  useEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    let scene: THREE.Scene;
    let camera: THREE.PerspectiveCamera;
    let renderer: THREE.WebGLRenderer;

    try {
      const setup = createScene(container);
      scene = setup.scene;
      camera = setup.camera;
      renderer = setup.renderer;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro desconhecido ao criar WebGL.';
      setWebglError(message);
      console.error('Falha ao criar cena WebGL:', err);
      return;
    }

    setWebglError(null);
    const cleanupList: Array<() => void> = [];

    scene.add(createGround());
    scene.add(createGridHelper());
    for (const wall of createArenaWalls()) {
      scene.add(wall);
    }

    for (const obj of createArenaObjects()) {
      scene.add(obj);
    }

    const robotGroup = createRobot();
    scene.add(robotGroup);

    const engine = new SimulatorEngine(robotGroup);
    const cameraController = createCameraController({
      canvas: renderer.domElement,
      camera,
      robotGroup,
    });

    const publishSnapshot = () => {
      onSnapshotChangeRef.current(engine.getSnapshot());
    };

    publishSnapshot();

    let previewRenderTarget: THREE.WebGLRenderTarget | null = null;
    let previewCamera: THREE.PerspectiveCamera | null = null;
    let previewCtx: CanvasRenderingContext2D | null = null;
    let previewPixelBuffer: Uint8Array | null = null;

    let animationFrame = 0;
    let lastPreviewTime = 0;

    const animate = () => {
      animationFrame = requestAnimationFrame(animate);
      engine.step();
      cameraController.update();
      renderer.render(scene, camera);

      const now = performance.now();
      if (
        previewRenderTarget &&
        previewCamera &&
        previewCtx &&
        now - lastPreviewTime >= PREVIEW_THROTTLE_MS
      ) {
        lastPreviewTime = now;

        const wasVisible = robotGroup.visible;
        robotGroup.visible = false;

        const snapshot = engine.getSnapshot();
        const rad = (snapshot.rotation * Math.PI) / 180;
        const frontX = Math.sin(rad);
        const frontZ = Math.cos(rad);
        const camHeight = 3;
        const camForward = 12;

        previewCamera.position.set(
          robotGroup.position.x + frontX * camForward,
          camHeight,
          robotGroup.position.z + frontZ * camForward,
        );
        previewCamera.lookAt(
          robotGroup.position.x + frontX * 200,
          camHeight,
          robotGroup.position.z + frontZ * 200,
        );

        renderer.setRenderTarget(previewRenderTarget);
        renderer.render(scene, previewCamera);
        renderer.setRenderTarget(null);

        const buffer = previewPixelBuffer!;
        renderer.readRenderTargetPixels(
          previewRenderTarget,
          0,
          0,
          PREVIEW_WIDTH,
          PREVIEW_HEIGHT,
          buffer,
        );

        const imageData = previewCtx.createImageData(PREVIEW_WIDTH, PREVIEW_HEIGHT);
        const data = imageData.data;
        const stride = PREVIEW_WIDTH * 4;
        for (let y = 0; y < PREVIEW_HEIGHT; y++) {
          const srcRow = PREVIEW_HEIGHT - 1 - y;
          const srcOffset = srcRow * stride;
          const dstOffset = y * stride;
          for (let x = 0; x < stride; x++) {
            data[dstOffset + x] = buffer[srcOffset + x];
          }
        }
        previewCtx.putImageData(imageData, 0, 0);

        robotGroup.visible = wasVisible;
      }

      publishSnapshot();
    };
    animate();

    const onResize = () => resizeScene(container, camera, renderer);
    window.addEventListener('resize', onResize);
    cleanupList.push(() => window.removeEventListener('resize', onResize));

    const handle: SimulatorCanvasHandle = {
      toggleCamera() {
        const enabled = cameraController.toggleMode();
        if (!enabled) {
          cameraController.animateToDefault();
        }
        return enabled;
      },
      async handleRemoteEvent(event) {
        if (event.type === 'execute') {
          const message = await engine.executeSequence(event.command);
          publishSnapshot();
          return message;
        }

        if (event.type === 'reset') {
          engine.reset();
          publishSnapshot();
          return { kind: 'info', text: 'Simulador reiniciado.' };
        }

        if (event.type === 'disconnect') {
          return { kind: 'error', text: event.reason };
        }

        return null;
      },
      getSnapshot() {
        return {
          ...engine.getSnapshot(),
          updatedAt: new Date().toISOString(),
        };
      },
      bindPreviewCanvas(canvas: HTMLCanvasElement) {
        if (previewRenderTarget) {
          previewRenderTarget.dispose();
          previewRenderTarget = null;
        }

        previewCtx = canvas.getContext('2d');
        if (!previewCtx) {
          console.error('Falha ao obter contexto 2D para preview.');
          return;
        }

        previewCamera = new THREE.PerspectiveCamera(100, PREVIEW_WIDTH / PREVIEW_HEIGHT, 0.1, 1500);
        previewRenderTarget = new THREE.WebGLRenderTarget(PREVIEW_WIDTH, PREVIEW_HEIGHT);
        previewPixelBuffer = new Uint8Array(PREVIEW_WIDTH * PREVIEW_HEIGHT * 4);
      },
      unbindPreviewCanvas() {
        if (previewRenderTarget) {
          previewRenderTarget.dispose();
          previewRenderTarget = null;
        }
        previewCamera = null;
        previewCtx = null;
        previewPixelBuffer = null;
      },
    };

    onReadyRef.current(handle);

    cleanupList.push(() => cancelAnimationFrame(animationFrame));
    cleanupList.push(() => cameraController.dispose());
    cleanupList.push(() => {
      renderer.dispose();
      const gl = renderer.getContext();
      const loseCtxExt = gl.getExtension('WEBGL_lose_context');
      if (loseCtxExt) {
        loseCtxExt.loseContext();
      }
    });
    cleanupList.push(() => {
      if (previewRenderTarget) {
        previewRenderTarget.dispose();
        previewRenderTarget = null;
      }
      previewCamera = null;
      previewCtx = null;
      previewPixelBuffer = null;
    });
    cleanupList.push(() => {
      for (const child of [...scene.children]) {
        if (child instanceof THREE.Mesh) {
          child.geometry.dispose();
          const material = child.material;
          if (Array.isArray(material)) {
            material.forEach((entry) => entry.dispose());
          } else {
            material.dispose();
          }
        }
      }
    });

    return () => {
      cleanupList.forEach((cleanup) => cleanup());
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  if (webglError) {
    return (
      <div className="simulator-canvas simulator-canvas--error">
        <p>Falha ao inicializar WebGL: {webglError}</p>
        <p>Tente recarregar a pagina ou use um navegador com suporte a WebGL.</p>
      </div>
    );
  }

  return <div ref={containerRef} className="simulator-canvas" />;
}