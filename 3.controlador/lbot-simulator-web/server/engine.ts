import * as CANNON from "cannon-es";
import { randomUUID } from "node:crypto";
import {
  ARENA_OBJECTS,
  PHYSICAL_WALLS,
  type ArenaObject,
} from "../shared/arena-objects.js";
import {
  parseLbmlSequence,
  normalizeLbml,
  type ParsedCommand,
} from "../shared/lbml.js";
import type {
  CommandResponse,
  CommandStatus,
  ExecuteCommandRequest,
  SimulatorStateSnapshot,
  SensorsResponse,
} from "../shared/protocol.js";

interface Motion {
  kind: "distance" | "rotation";
  value: number;
  direction: number;
}
interface Running {
  record: CommandResponse;
  motions: Motion[];
  motion: Motion | null;
  progress: number;
  stalled: number;
}
const DT = 1 / 60;
const RAD = Math.PI / 180;
const TERMINAL = new Set<CommandStatus>([
  "completed",
  "blocked",
  "cancelled",
  "failed",
  "timed_out",
]);
export class Simulation {
  readonly world = new CANNON.World({ gravity: new CANNON.Vec3(0, -9.81, 0) });
  readonly body: CANNON.Body;
  session = randomUUID();
  revision = 0;
  yaw = 0;
  private running: Running | null = null;
  private last: CommandResponse | null = null;
  private commands = new Map<string, CommandResponse>();
  private contact = false;
  constructor(
    readonly objects: ArenaObject[] = ARENA_OBJECTS,
    private onCommand: (
      event: "accepted" | "terminal",
      record: CommandResponse,
    ) => void = () => {},
  ) {
    this.world.defaultContactMaterial.friction = 0;
    this.body = new CANNON.Body({
      mass: 1,
      shape: new CANNON.Box(new CANNON.Vec3(0.1, 0.06, 0.15)),
      fixedRotation: true,
      linearDamping: 0,
    });
    this.body.position.set(0, 0.06, 0);
    this.world.addBody(this.body);
    const ground = new CANNON.Body({ mass: 0, shape: new CANNON.Plane() });
    ground.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
    this.world.addBody(ground);
    for (const w of PHYSICAL_WALLS)
      this.addStatic(
        new CANNON.Box(
          new CANNON.Vec3(w.width / 200, w.height / 200, w.depth / 200),
        ),
        w.x / 100,
        w.height / 200,
        w.z / 100,
      );
    for (const o of this.objects) {
      if (o.type === "cube") {
        const s = o.size as { width: number; height: number; depth: number };
        this.addStatic(
          new CANNON.Box(
            new CANNON.Vec3(s.width / 200, s.height / 200, s.depth / 200),
          ),
          o.x / 100,
          s.height / 200,
          o.z / 100,
        );
      } else if (o.type === "sphere") {
        const s = o.size as { radius: number };
        this.addStatic(
          new CANNON.Sphere(s.radius / 100),
          o.x / 100,
          s.radius / 100,
          o.z / 100,
        );
      } else {
        const s = o.size as { radius: number; height: number };
        const shape = new CANNON.Cylinder(
          0,
          s.radius / 100,
          s.height / 100,
          24,
        );
        this.addStatic(shape, o.x / 100, s.height / 200, o.z / 100);
      }
    }
    this.body.addEventListener("collide", (e: { body: CANNON.Body }) => {
      if (e.body !== ground) this.contact = true;
    });
  }
  private addStatic(shape: CANNON.Shape, x: number, y: number, z: number) {
    const b = new CANNON.Body({ mass: 0, shape });
    b.position.set(x, y, z);
    b.aabbNeedsUpdate = true;
    this.world.addBody(b);
  }
  submit(req: ExecuteCommandRequest): CommandResponse {
    if (req.session_id && req.session_id !== this.session)
      throw new Error("stale_session");
    const id = req.command_id ?? randomUUID();
    const command = normalizeLbml(req.command);
    const previous = this.commands.get(id);
    if (previous) {
      if (previous.command !== command || previous.session_id !== this.session)
        throw new Error("id_conflict");
      return { ...previous };
    }
    if (this.running) throw new Error("busy");
    const parsed = parseLbmlSequence(command);
    if (
      !parsed?.length ||
      parsed.length > 64 ||
      parsed.some((c) => c.value <= 0 || c.value > (c.type === "D" ? 400 : 720))
    )
      throw new Error("invalid_command");
    const record: CommandResponse = {
      accepted: true,
      command,
      command_id: id,
      session_id: this.session,
      status: "accepted",
      source: req.source ?? "http",
      distance_cm: 0,
      rotation_degrees: 0,
      revision: ++this.revision,
    };
    this.commands.set(id, record);
    this.last = record;
    if (this.commands.size > 1000)
      this.commands.delete(this.commands.keys().next().value!);
    this.running = {
      record,
      motions: parsed.flatMap((c) => this.expand(c)),
      motion: null,
      progress: 0,
      stalled: 0,
    };
    this.onCommand("accepted", { ...record });
    return { ...record };
  }
  private expand(c: ParsedCommand): Motion[] {
    if (c.type === "R")
      return [
        {
          kind: "rotation",
          value: c.value,
          direction: c.direction === "L" ? 1 : -1,
        },
      ];
    const move: Motion = {
      kind: "distance",
      value: c.value / 100,
      direction: c.direction === "B" ? -1 : 1,
    };
    return c.direction === "L" || c.direction === "R"
      ? [
          {
            kind: "rotation",
            value: 90,
            direction: c.direction === "L" ? 1 : -1,
          },
          move,
        ]
      : [move];
  }
  tick(dt = DT) {
    const r = this.running;
    if (!r) {
      this.revision++;
      return;
    }
    r.record.status = "running";
    if (!r.motion) {
      r.motion = r.motions.shift() ?? null;
      r.progress = 0;
      r.stalled = 0;
    }
    if (!r.motion) {
      this.finish("completed");
      return;
    }
    const m = r.motion;
    const previousX = this.body.position.x,
      previousZ = this.body.position.z;
    const previousYaw = this.yaw;
    const remaining = Math.max(0, m.value - r.progress);
    if (m.kind === "distance") {
      const speed = Math.min(0.3, remaining / dt) * m.direction;
      this.body.velocity.set(
        Math.sin(this.yaw * RAD) * speed,
        0,
        Math.cos(this.yaw * RAD) * speed,
      );
    } else {
      this.body.velocity.set(0, 0, 0);
      this.yaw += Math.min(90 * dt, remaining) * m.direction;
    }
    this.body.quaternion.setFromAxisAngle(
      new CANNON.Vec3(0, 1, 0),
      this.yaw * RAD,
    );
    this.contact = false;
    this.body.aabbNeedsUpdate = true;
    this.world.step(dt);
    this.body.position.y = 0.06;
    this.body.velocity.y = 0;
    this.revision++;
    const progress =
      m.kind === "distance"
        ? Math.max(
            0,
            ((this.body.position.x - previousX) * Math.sin(this.yaw * RAD) +
              (this.body.position.z - previousZ) * Math.cos(this.yaw * RAD)) *
              m.direction,
          )
        : Math.abs(this.yaw - previousYaw);
    r.progress += progress;
    if (m.kind === "distance") r.record.distance_cm += progress * 100;
    else r.record.rotation_degrees += this.yaw - previousYaw;
    r.record.revision = this.revision;
    if (this.contact) {
      this.finish("blocked", "collision");
      return;
    }
    if (progress < 1e-6) r.stalled += dt;
    else r.stalled = 0;
    if (r.stalled >= 1) {
      this.finish("blocked", "no_progress");
      return;
    }
    if (r.progress >= m.value - (m.kind === "distance" ? 0.001 : 0.05)) {
      this.body.velocity.set(0, 0, 0);
      r.motion = null;
      if (!r.motions.length) this.finish("completed");
    }
  }
  private finish(status: CommandStatus, reason?: string) {
    if (this.running) {
      Object.assign(this.running.record, {
        status,
        reason,
        revision: ++this.revision,
      });
      this.last = this.running.record;
      this.onCommand("terminal", { ...this.running.record });
    }
    this.running = null;
    this.body.velocity.set(0, 0, 0);
    this.body.angularVelocity.set(0, 0, 0);
  }
  stop(reason = "stop_requested") {
    this.finish("cancelled", reason);
    return this.snapshot();
  }
  reset(pose = { x: 0, z: 0, rotation: 0 }) {
    if (
      ![pose.x, pose.z, pose.rotation].every(Number.isFinite) ||
      Math.abs(pose.x) > 180 ||
      Math.abs(pose.z) > 180
    )
      throw new Error("invalid_spawn");
    this.stop("reset");
    this.session = randomUUID();
    this.revision++;
    this.yaw = pose.rotation;
    this.body.position.set(pose.x / 100, 0.06, pose.z / 100);
    this.body.quaternion.setFromAxisAngle(
      new CANNON.Vec3(0, 1, 0),
      this.yaw * RAD,
    );
    this.body.aabbNeedsUpdate = true;
    this.last = null;
    return this.snapshot();
  }
  getCommand(id: string) {
    const r = this.commands.get(id);
    return r ? { ...r } : null;
  }
  snapshot(): SimulatorStateSnapshot {
    return {
      x: this.body.position.x * 100,
      z: this.body.position.z * 100,
      rotation: this.yaw,
      currentCommand: this.running?.record.command ?? "-",
      isAnimating: !!this.running,
      updatedAt: new Date().toISOString(),
      session_id: this.session,
      revision: this.revision,
      operation: this.last ? { ...this.last } : null,
    };
  }
  sensors(): SensorsResponse {
    const ray = (sign: number) => {
      const dx = Math.sin(this.yaw * RAD) * sign,
        dz = Math.cos(this.yaw * RAD) * sign;
      const from = new CANNON.Vec3(
        this.body.position.x + dx * 0.151,
        0.06,
        this.body.position.z + dz * 0.151,
      );
      const to = new CANNON.Vec3(from.x + dx * 4, 0.06, from.z + dz * 4);
      const result = new CANNON.RaycastResult();
      this.world.raycastClosest(from, to, { skipBackfaces: true }, result);
      return result.hasHit ? Math.min(400, result.distance * 100) : 400;
    };
    const readings = { frente: ray(1), tras: ray(-1) };
    return {
      connected: true,
      readings,
      session_id: this.session,
      revision: this.revision,
      captured_at: new Date().toISOString(),
      validity: {
        frente: readings.frente >= 400 ? "out_of_range" : "valid",
        tras: readings.tras >= 400 ? "out_of_range" : "valid",
      },
    };
  }
}
export { TERMINAL };
