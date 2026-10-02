import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import type {
  ServerEvent,
  SimulatorStateSnapshot,
} from "../../shared/protocol.js";
import { createCameraController } from "../simulator/camera.js";
import { createRobot } from "../simulator/robot.js";
import { createScene, resizeScene } from "../simulator/scene.js";
import { populateWorld } from "../simulator/render-world.js";
import type { SimulatorSnapshot, StatusMessage } from "../simulator/types.js";
export interface SimulatorCanvasHandle {
  toggleCamera: () => boolean;
  handleRemoteEvent: (event: ServerEvent) => Promise<StatusMessage | null>;
  getSnapshot: () => SimulatorStateSnapshot;
}
export function SimulatorCanvas({
  onReady,
  onSnapshotChange,
}: {
  onReady: (handle: SimulatorCanvasHandle) => void;
  onSnapshotChange: (snapshot: SimulatorSnapshot) => void;
}) {
  const root = useRef<HTMLDivElement>(null),
    callbacks = useRef({ onReady, onSnapshotChange });
  callbacks.current = { onReady, onSnapshotChange };
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    if (!root.current) return;
    const container = root.current;
    let setup: ReturnType<typeof createScene>;
    try {
      setup = createScene(container);
    } catch (e) {
      setError(String(e));
      return;
    }
    const { scene, camera, renderer, robotHeadlight } = setup;
    const world = new THREE.Group();
    scene.add(world);
    populateWorld(world);
    const robot = createRobot();
    scene.add(robot);
    const controls = createCameraController({
      canvas: renderer.domElement,
      camera,
      robotGroup: robot,
    });
    let snapshot: SimulatorStateSnapshot = {
      x: 0,
      z: 0,
      rotation: 0,
      currentCommand: "-",
      isAnimating: false,
      updatedAt: "",
      session_id: "",
      revision: 0,
      operation: null,
    };
    let frame = 0,
      disposed = false;
    function animate() {
      if (disposed) return;
      frame = requestAnimationFrame(animate);
      controls.update();
      robotHeadlight.position.set(snapshot.x, 3, snapshot.z);
      renderer.render(scene, camera);
    }
    animate();
    callbacks.current.onReady({
      toggleCamera() {
        const enabled = controls.toggleMode();
        if (!enabled) controls.animateToDefault();
        return enabled;
      },
      async handleRemoteEvent(event) {
        if (event.type === "scene") {
          world.traverse((o) => {
            if (o instanceof THREE.Mesh) {
              o.geometry.dispose();
              for (const m of Array.isArray(o.material)
                ? o.material
                : [o.material])
                m.dispose();
            }
          });
          world.clear();
          populateWorld(world, event.objects);
        }
        if (event.type === "state") {
          snapshot = event.state;
          robot.position.set(snapshot.x, 6, snapshot.z);
          robot.rotation.y = (snapshot.rotation * Math.PI) / 180;
          callbacks.current.onSnapshotChange(snapshot);
          const op = snapshot.operation;
          if (op && !snapshot.isAnimating)
            return {
              kind: op.status === "completed" ? "info" : "error",
              text: `${op.status}${op.reason ? ": " + op.reason : ""} (${op.distance_cm.toFixed(1)} cm)`,
            };
        }
        return null;
      },
      getSnapshot: () => ({ ...snapshot }),
    });
    const resize = () => resizeScene(container, camera, renderer);
    window.addEventListener("resize", resize);
    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", resize);
      controls.dispose();
      scene.traverse((o) => {
        if (o instanceof THREE.Mesh) {
          o.geometry.dispose();
          for (const m of Array.isArray(o.material) ? o.material : [o.material])
            m.dispose();
        }
      });
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, []);
  return error ? (
    <div role="alert">Falha ao inicializar WebGL: {error}</div>
  ) : (
    <div ref={root} className="simulator-canvas" />
  );
}
