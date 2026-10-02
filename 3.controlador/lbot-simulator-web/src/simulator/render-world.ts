import type { ArenaObject } from "../../shared/arena-objects.js";
import * as THREE from "three";
import { createGround, createArenaWalls } from "./arena.js";
import { createArenaObjects } from "./objects.js";
import { CAMERA } from "../../shared/camera-config.js";
import type { SimulatorStateSnapshot } from "../../shared/protocol.js";
export function populateWorld(scene: THREE.Object3D, objects?: ArenaObject[]) {
  scene.add(
    createGround(),
    ...createArenaWalls(),
    ...createArenaObjects(objects),
  );
}
export function configureRobotCamera(
  camera: THREE.PerspectiveCamera,
  state: SimulatorStateSnapshot,
) {
  const rad = (state.rotation * Math.PI) / 180,
    dx = Math.sin(rad),
    dz = Math.cos(rad);
  camera.fov = CAMERA.verticalFov;
  camera.aspect = CAMERA.width / CAMERA.height;
  camera.updateProjectionMatrix();
  camera.position.set(
    state.x + dx * CAMERA.forwardCm,
    CAMERA.heightCm,
    state.z + dz * CAMERA.forwardCm,
  );
  camera.lookAt(state.x + dx * 200, CAMERA.heightCm, state.z + dz * 200);
}
