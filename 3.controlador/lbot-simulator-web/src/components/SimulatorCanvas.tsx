import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import type { ServerEvent, SimulatorStateSnapshot } from '../../shared/protocol.js';
import { createArenaWalls, createGridHelper, createGround } from '../simulator/arena.js';
import { createCameraController } from '../simulator/camera.js';
import { createArenaObjects } from '../simulator/objects.js';
import { SimulatorEngine } from '../simulator/engine.js';
import { createRobot } from '../simulator/robot.js';
import { createScene, resizeScene } from '../simulator/scene.js';
import type { SimulatorSnapshot, StatusMessage } from '../simulator/types.js';

export interface SimulatorCanvasHandle {
  toggleCamera: () => boolean;
  handleRemoteEvent: (event: ServerEvent) => Promise<StatusMessage | null>;
  getSnapshot: () => SimulatorStateSnapshot;
}

interface SimulatorCanvasProps {
  onReady: (handle: SimulatorCanvasHandle) => void;
  onSnapshotChange: (snapshot: SimulatorSnapshot) => void;
}

export function SimulatorCanvas({ onReady, onSnapshotChange }: SimulatorCanvasProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    const { scene, camera, renderer } = createScene(container);
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
      onSnapshotChange(engine.getSnapshot());
    };

    publishSnapshot();

    let animationFrame = 0;
    const animate = () => {
      animationFrame = requestAnimationFrame(animate);
      engine.step();
      cameraController.update();
      renderer.render(scene, camera);
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
    };

    onReady(handle);

    cleanupList.push(() => cancelAnimationFrame(animationFrame));
    cleanupList.push(() => cameraController.dispose());
    cleanupList.push(() => renderer.dispose());
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
      container.removeChild(renderer.domElement);
    };
  }, [onReady, onSnapshotChange]);

  return <div ref={containerRef} className="simulator-canvas" />;
}
