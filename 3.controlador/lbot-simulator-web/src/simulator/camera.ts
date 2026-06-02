import * as THREE from 'three';
import { getDefaultCameraPosition } from './scene.js';

export interface CameraController {
  canvas: HTMLCanvasElement;
  camera: THREE.PerspectiveCamera;
  robotGroup: THREE.Group;
}

export interface CameraHandle {
  dispose: () => void;
  isThirdPersonView: () => boolean;
  toggleMode: () => boolean;
  update: () => void;
  animateToDefault: () => void;
}

export function createCameraController({ canvas, camera, robotGroup }: CameraController): CameraHandle {
  const mouse = { x: 0, y: 0, isDown: false };
  const state = { isThirdPersonView: false };

  const onMouseDown = () => {
    mouse.isDown = true;
  };

  const onMouseUp = () => {
    mouse.isDown = false;
  };

  const onMouseMove = (event: MouseEvent) => {
    if (!mouse.isDown) {
      return;
    }

    const rect = canvas.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  };

  canvas.addEventListener('mousedown', onMouseDown);
  window.addEventListener('mouseup', onMouseUp);
  canvas.addEventListener('mousemove', onMouseMove);

  return {
    dispose() {
      canvas.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mouseup', onMouseUp);
      canvas.removeEventListener('mousemove', onMouseMove);
    },
    isThirdPersonView() {
      return state.isThirdPersonView;
    },
    toggleMode() {
      state.isThirdPersonView = !state.isThirdPersonView;
      return state.isThirdPersonView;
    },
    update() {
      if (state.isThirdPersonView) {
        const rotation = robotGroup.rotation.y;
        const targetX = robotGroup.position.x - Math.sin(rotation) * 60;
        const targetY = 30;
        const targetZ = robotGroup.position.z - Math.cos(rotation) * 60;
        camera.position.x += (targetX - camera.position.x) * 0.1;
        camera.position.y += (targetY - camera.position.y) * 0.1;
        camera.position.z += (targetZ - camera.position.z) * 0.1;
        camera.lookAt(robotGroup.position.x, 0, robotGroup.position.z);
        return;
      }

      if (!mouse.isDown) {
        return;
      }

      const angle = mouse.x * Math.PI;
      camera.position.x = 160 * Math.cos(angle);
      camera.position.z = 280 * Math.sin(angle);
      camera.position.y = 160 + mouse.y * 80;
      camera.lookAt(robotGroup.position);
    },
    animateToDefault() {
      const target = getDefaultCameraPosition();
      const start = { x: camera.position.x, y: camera.position.y, z: camera.position.z };
      const startTime = performance.now();

      const tick = () => {
        const elapsed = performance.now() - startTime;
        const progress = Math.min(elapsed / 1000, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        camera.position.x = start.x + (target.x - start.x) * eased;
        camera.position.y = start.y + (target.y - start.y) * eased;
        camera.position.z = start.z + (target.z - start.z) * eased;
        camera.lookAt(0, 0, 0);

        if (progress < 1) {
          requestAnimationFrame(tick);
        }
      };

      requestAnimationFrame(tick);
    },
  };
}
