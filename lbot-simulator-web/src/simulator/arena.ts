import * as THREE from 'three';

export function createGround(): THREE.Mesh {
  const texture = new THREE.TextureLoader().load(
    'data:image/svg+xml;base64,' +
      btoa(`
      <svg width="64" height="64" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grass" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse">
            <rect width="8" height="8" fill="#228B22"/>
            <path d="M2,8 Q2,6 1,4 Q2,2 3,0" stroke="#32CD32" stroke-width="0.5" fill="none"/>
            <path d="M4,8 Q4,6 5,4 Q4,2 3,0" stroke="#32CD32" stroke-width="0.5" fill="none"/>
            <path d="M6,8 Q6,6 7,4 Q6,2 5,0" stroke="#32CD32" stroke-width="0.5" fill="none"/>
          </pattern>
        </defs>
        <rect width="64" height="64" fill="url(#grass)"/>
      </svg>
    `),
  );

  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(100, 100);

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(800, 800),
    new THREE.MeshLambertMaterial({ map: texture, color: 0x90ee90 }),
  );
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  return ground;
}

export function createGridHelper(): THREE.GridHelper {
  const helper = new THREE.GridHelper(800, 80, 0x4caf50, 0x90ee90);
  const material = helper.material as THREE.Material & { opacity: number; transparent: boolean };
  material.opacity = 0.3;
  material.transparent = true;
  return helper;
}

export function createArenaWalls(): THREE.Mesh[] {
  const material = new THREE.MeshStandardMaterial({
    color: 0x8b4513,
    roughness: 0.85,
    metalness: 0.1,
  });

  const wallHeight = 15;
  const wallThickness = 8;
  const arenaSize = 400;
  const definitions = [
    { width: arenaSize + wallThickness, depth: wallThickness, x: 0, z: arenaSize / 2 + wallThickness / 2 },
    { width: arenaSize + wallThickness, depth: wallThickness, x: 0, z: -arenaSize / 2 - wallThickness / 2 },
    { width: wallThickness, depth: arenaSize, x: arenaSize / 2 + wallThickness / 2, z: 0 },
    { width: wallThickness, depth: arenaSize, x: -arenaSize / 2 - wallThickness / 2, z: 0 },
  ];

  return definitions.map(({ width, depth, x, z }) => {
    const wall = new THREE.Mesh(new THREE.BoxGeometry(width, wallHeight, depth), material);
    wall.position.set(x, wallHeight / 2, z);
    wall.castShadow = true;
    wall.receiveShadow = true;
    return wall;
  });
}
