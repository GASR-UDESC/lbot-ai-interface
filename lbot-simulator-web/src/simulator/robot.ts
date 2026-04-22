import * as THREE from 'three';

export function createRobot(): THREE.Group {
  const robotGroup = new THREE.Group();

  const add = (mesh: THREE.Object3D) => robotGroup.add(mesh);

  const chassis = new THREE.Mesh(
    new THREE.BoxGeometry(20, 4, 30),
    new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.7, roughness: 0.3 }),
  );
  chassis.position.y = -4;
  chassis.castShadow = true;
  add(chassis);

  const body = new THREE.Mesh(
    new THREE.BoxGeometry(18, 8, 25),
    new THREE.MeshStandardMaterial({ color: 0x3498db, metalness: 0.6, roughness: 0.4 }),
  );
  body.position.y = 2;
  body.castShadow = true;
  add(body);

  const hood = new THREE.Mesh(
    new THREE.BoxGeometry(16, 3, 8),
    new THREE.MeshStandardMaterial({ color: 0xe74c3c, metalness: 0.5, roughness: 0.3 }),
  );
  hood.position.set(0, 6.5, 8);
  hood.castShadow = true;
  add(hood);

  const windshield = new THREE.Mesh(
    new THREE.BoxGeometry(16, 6, 1),
    new THREE.MeshStandardMaterial({
      color: 0x87ceeb,
      metalness: 0.1,
      roughness: 0.1,
      transparent: true,
      opacity: 0.7,
    }),
  );
  windshield.position.set(0, 5, 4);
  windshield.rotation.x = -0.2;
  add(windshield);

  for (const x of [-6, 6]) {
    const headlight = new THREE.Mesh(
      new THREE.CylinderGeometry(2, 2, 1, 12),
      new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffaa, emissiveIntensity: 0.5 }),
    );
    headlight.rotation.z = Math.PI / 2;
    headlight.position.set(x, 3, 15.5);
    add(headlight);
  }

  const grill = new THREE.Mesh(
    new THREE.BoxGeometry(12, 4, 0.5),
    new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.8, roughness: 0.2 }),
  );
  grill.position.set(0, 1, 15.2);
  add(grill);

  for (const [x, z] of [
    [-11, 10],
    [11, 10],
    [-11, -10],
    [11, -10],
  ]) {
    const wheel = new THREE.Mesh(
      new THREE.CylinderGeometry(4, 4, 3, 16),
      new THREE.MeshStandardMaterial({ color: 0x2c3e50, metalness: 0.8, roughness: 0.2 }),
    );
    wheel.rotation.z = Math.PI / 2;
    wheel.position.set(x, -2, z);
    wheel.castShadow = true;
    add(wheel);

    const detail = new THREE.Mesh(
      new THREE.CylinderGeometry(2.5, 2.5, 3.5, 8),
      new THREE.MeshStandardMaterial({ color: 0x95a5a6, metalness: 0.9, roughness: 0.1 }),
    );
    detail.rotation.z = Math.PI / 2;
    detail.position.set(x, -2, z);
    add(detail);
  }

  const antenna = new THREE.Mesh(
    new THREE.CylinderGeometry(0.3, 0.3, 6, 8),
    new THREE.MeshStandardMaterial({ color: 0x95a5a6, metalness: 0.8, roughness: 0.2 }),
  );
  antenna.position.set(0, 9, -5);
  add(antenna);

  const antennaLed = new THREE.Mesh(
    new THREE.SphereGeometry(1, 8, 6),
    new THREE.MeshStandardMaterial({ color: 0xff0000, emissive: 0xff0000, emissiveIntensity: 0.4 }),
  );
  antennaLed.position.set(0, 12, -5);
  add(antennaLed);

  const arrow = new THREE.Mesh(
    new THREE.ConeGeometry(2, 4, 8),
    new THREE.MeshStandardMaterial({
      color: 0xffff00,
      metalness: 0.5,
      roughness: 0.3,
      emissive: 0xffff00,
      emissiveIntensity: 0.3,
    }),
  );
  arrow.rotation.x = Math.PI / 2;
  arrow.position.set(0, 7, 12);
  add(arrow);

  return robotGroup;
}
