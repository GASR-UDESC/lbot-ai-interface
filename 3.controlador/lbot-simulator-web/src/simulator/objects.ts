import * as THREE from "three";
import { ARENA_OBJECTS, type ArenaObject } from "../../shared/arena-objects.js";

export function createArenaObjects(
  objects: ArenaObject[] = ARENA_OBJECTS,
): THREE.Mesh[] {
  const meshes: THREE.Mesh[] = [];

  for (const obj of objects) {
    let geometry: THREE.BufferGeometry;
    let yPos: number;

    if (obj.type === "cube") {
      const s = obj.size as { width: number; height: number; depth: number };
      geometry = new THREE.BoxGeometry(s.width, s.height, s.depth);
      yPos = s.height / 2;
    } else if (obj.type === "sphere") {
      const s = obj.size as { radius: number };
      geometry = new THREE.SphereGeometry(s.radius, 32, 32);
      yPos = s.radius;
    } else {
      // cone
      const s = obj.size as { radius: number; height: number };
      geometry = new THREE.ConeGeometry(s.radius, s.height, 32);
      yPos = s.height / 2;
    }

    const material = new THREE.MeshStandardMaterial({ color: obj.color });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(obj.x, yPos, obj.z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    meshes.push(mesh);
  }

  return meshes;
}
