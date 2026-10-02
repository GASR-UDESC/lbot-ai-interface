import * as THREE from "three";
import type { ArenaObject } from "../shared/arena-objects.js";
import { createScene } from "./simulator/scene.js";
import {
  populateWorld,
  configureRobotCamera,
} from "./simulator/render-world.js";
import { CAMERA } from "../shared/camera-config.js";
import type { SimulatorStateSnapshot } from "../shared/protocol.js";
const root = document.querySelector<HTMLDivElement>("#camera")!;
root.style.width = `${CAMERA.width}px`;
root.style.height = `${CAMERA.height}px`;
const { scene, camera, renderer, robotHeadlight } = createScene(root);
scene.fog = null;
const world = new THREE.Group();
scene.add(world);
populateWorld(world);
let config = "";
renderer.setPixelRatio(1);
renderer.setSize(CAMERA.width, CAMERA.height);
Object.assign(window, {
  renderRobotFrame(state: SimulatorStateSnapshot, objects: ArenaObject[]) {
    const next = JSON.stringify(objects);
    if (next !== config) {
      world.traverse((o) => {
        if (o instanceof THREE.Mesh) {
          o.geometry.dispose();
          for (const m of Array.isArray(o.material) ? o.material : [o.material])
            m.dispose();
        }
      });
      world.clear();
      populateWorld(world, objects);
      config = next;
    }
    configureRobotCamera(camera, state);
    robotHeadlight.position.copy(camera.position);
    renderer.render(scene, camera);
    return renderer.domElement.toDataURL("image/png").split(",")[1];
  },
});
