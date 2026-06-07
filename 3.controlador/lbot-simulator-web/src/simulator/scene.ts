import * as THREE from 'three';

export interface SceneSetup {
  scene: THREE.Scene;
  camera: THREE.PerspectiveCamera;
  renderer: THREE.WebGLRenderer;
  robotHeadlight: THREE.PointLight;
}

const SKY_COLOR = 0x87ceeb;
const CAMERA_DEFAULT = { x: 120, y: 160, z: 240 };

export function createScene(container: HTMLDivElement): SceneSetup {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(SKY_COLOR);
  scene.fog = new THREE.Fog(SKY_COLOR, 200, 800);

  const camera = new THREE.PerspectiveCamera(
    75,
    container.clientWidth / container.clientHeight,
    0.1,
    1500,
  );
  camera.position.set(CAMERA_DEFAULT.x, CAMERA_DEFAULT.y, CAMERA_DEFAULT.z);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.4;

  scene.add(new THREE.AmbientLight(0xffffff, 1.2));

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
  directionalLight.position.set(50, 150, 50);
  directionalLight.castShadow = true;
  directionalLight.shadow.camera.left = -400;
  directionalLight.shadow.camera.right = 400;
  directionalLight.shadow.camera.top = 400;
  directionalLight.shadow.camera.bottom = -400;
  directionalLight.shadow.camera.near = 1;
  directionalLight.shadow.camera.far = 500;
  directionalLight.shadow.mapSize.width = 2048;
  directionalLight.shadow.mapSize.height = 2048;
  scene.add(directionalLight);

  scene.add(new THREE.HemisphereLight(0x87ceeb, 0x228b22, 0.8));

  const robotHeadlight = new THREE.PointLight(0xffffff, 5.0, 120, 1.5);
  robotHeadlight.position.set(0, 3, 0);
  scene.add(robotHeadlight);

  container.appendChild(renderer.domElement);

  return { scene, camera, renderer, robotHeadlight };
}

export function resizeScene(
  container: HTMLDivElement,
  camera: THREE.PerspectiveCamera,
  renderer: THREE.WebGLRenderer,
): void {
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}

export function getDefaultCameraPosition(): Readonly<{ x: number; y: number; z: number }> {
  return CAMERA_DEFAULT;
}
