import cors from "cors";
import express from "express";
import { randomUUID } from "node:crypto";
import { resolve } from "node:path";
import { mkdir, appendFile } from "node:fs/promises";
import type { ArenaObject } from "../shared/arena-objects.js";
import { Simulation } from "./engine.js";
import { HeadlessSceneRenderer } from "./scene-renderer.js";
import { INTRINSICS, RANGE_PROJECTION } from "../shared/camera-config.js";
import type { ExecuteCommandRequest } from "../shared/protocol.js";
const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));
const port = Number(process.env.PORT ?? 3001);
let logging = Promise.resolve();
function trace(event: string, data: object) {
  const directory = process.env.LBOT_TRACE_DIR ?? resolve("runs");
  logging = logging
    .then(async () => {
      await mkdir(directory, { recursive: true });
      await appendFile(
        resolve(directory, "simulator.jsonl"),
        JSON.stringify({ at: Date.now() / 1000, event, ...data }) + "\n",
      );
    })
    .catch((e) => console.error("trace_unavailable:", String(e)));
}
function createSimulation(objects?: ArenaObject[]) {
  return new Simulation(objects, (event, record) => trace(event, record));
}
let sim = createSimulation();
const renderer = new HeadlessSceneRenderer(
  `http://127.0.0.1:${port}/camera.html`,
);
app.get("/api/health", (_req, res) =>
  res.json({ status: "online", session_id: sim.session }),
);
app.get("/api/status", (_req, res) =>
  res.json({
    connected: true,
    activeClientId: null,
    pendingEvents: 0,
    session_id: sim.session,
    operation: sim.snapshot().operation,
  }),
);
app.get("/api/state", (_req, res) =>
  res.json({ connected: true, activeClientId: null, state: sim.snapshot() }),
);
app.post("/api/state", (_req, res) =>
  res.status(405).json({ error: "server_authoritative" }),
);
app.get("/api/sensors", (_req, res) => res.json(sim.sensors()));
app.get("/api/camera", async (_req, res) => {
  const state = sim.snapshot();
  try {
    const image = await renderer.render(state, sim.objects);
    res.json({
      connected: true,
      image,
      format: "png",
      encoding: "base64",
      renderMethod: "webgl",
      frame_id: randomUUID(),
      session_id: state.session_id,
      revision: state.revision,
      captured_at: state.updatedAt,
      intrinsics: INTRINSICS,
      range_projection: RANGE_PROJECTION,
    });
  } catch (e) {
    res.status(503).json({
      connected: false,
      image: null,
      error: "camera_unavailable",
      detail: String(e),
    });
  }
});
app.post("/api/commands", (req, res) => {
  try {
    if (typeof req.body?.command !== "string")
      throw new Error("invalid_command");
    for (const field of ["command_id", "session_id"]) {
      const value = req.body[field];
      if (
        value !== undefined &&
        (typeof value !== "string" || !/^[a-zA-Z0-9_-]{1,128}$/.test(value))
      )
        throw new Error("invalid_identifier");
    }
    if (
      req.body.source !== undefined &&
      !["ui", "http"].includes(req.body.source)
    )
      throw new Error("invalid_source");
    res.json(sim.submit(req.body as ExecuteCommandRequest));
  } catch (e) {
    const error = (e as Error).message;
    res
      .status(
        ["busy", "stale_session", "id_conflict"].includes(error) ? 409 : 400,
      )
      .json({ error });
  }
});
app.get("/api/commands/:id", (req, res) => {
  const record = sim.getCommand(req.params.id);
  if (!record) res.status(404).json({ error: "unknown_command" });
  else res.json(record);
});
app.post("/api/stop", (_req, res) =>
  res.json({ status: "completed", state: sim.stop() }),
);
app.post("/api/reset", (req, res) => {
  const state = sim.reset();
  trace("reset", { session_id: state.session_id, revision: state.revision });
  res.json({
    accepted: true,
    session_id: state.session_id,
    source: req.body?.source ?? "http",
  });
});
app.post("/api/scenario", (req, res) => {
  if (process.env.LBOT_ENABLE_EVAL !== "1") {
    res.status(404).json({ error: "eval_disabled" });
    return;
  }
  const objects = req.body?.objects;
  if (
    !Array.isArray(objects) ||
    objects.length > 32 ||
    objects.some(
      (o) =>
        !o ||
        !["cube", "sphere", "cone"].includes(o.type) ||
        !Number.isFinite(o.x) ||
        !Number.isFinite(o.z) ||
        Math.abs(o.x) > 180 ||
        Math.abs(o.z) > 180 ||
        !/^#[0-9a-fA-F]{6}$/.test(o.color) ||
        typeof o.id !== "string" ||
        !o.id ||
        !o.size ||
        (o.type === "cube"
          ? ["width", "height", "depth"]
          : o.type === "sphere"
            ? ["radius"]
            : ["radius", "height"]
        ).some((k) => !Number.isFinite(o.size[k])) ||
        Object.values(o.size).some(
          (v) =>
            typeof v !== "number" || !Number.isFinite(v) || v <= 0 || v > 100,
        ),
    )
  ) {
    res.status(400).json({ error: "invalid_scenario" });
    return;
  }
  try {
    const next = createSimulation(objects);
    next.reset(req.body.pose);
    sim.stop("scenario_changed");
    sim = next;
    trace("scenario", { session_id: sim.session });
    res.json({ state: sim.snapshot() });
  } catch (e) {
    res.status(400).json({ error: String(e) });
  }
});
app.get("/api/events", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.flushHeaders();
  res.write(
    `data: ${JSON.stringify({ type: "ready", clientId: randomUUID() })}\n\n`,
  );
  let session = "";
  const publish = () => {
    if (session !== sim.session) {
      session = sim.session;
      res.write(
        `data: ${JSON.stringify({ type: "scene", objects: sim.objects })}\n\n`,
      );
    }
    res.write(
      `data: ${JSON.stringify({ type: "state", state: sim.snapshot() })}\n\n`,
    );
  };
  publish();
  const interval = setInterval(publish, 100);
  req.on("close", () => clearInterval(interval));
});
if (process.env.NODE_ENV === "production")
  app.use(express.static(resolve("dist")));
else {
  const { createServer } = await import("vite");
  const vite = await createServer({
    server: { middlewareMode: true, hmr: false },
    appType: "spa",
  });
  app.use(vite.middlewares);
}
let previous = performance.now(),
  accumulator = 0;
const ticker = setInterval(() => {
  const now = performance.now();
  accumulator += Math.min((now - previous) / 1000, 0.25);
  previous = now;
  while (accumulator >= 1 / 60) {
    sim.tick();
    accumulator -= 1 / 60;
  }
}, 8);
const server = app.listen(port, "127.0.0.1", () => {
  console.log(`Simulator API http://127.0.0.1:${port}`);
  void renderer
    .start()
    .catch((e) => console.error("camera_unavailable:", String(e)));
});
async function shutdown() {
  clearInterval(ticker);
  sim.stop("shutdown");
  await renderer.close();
  await logging;
  server.close();
  process.exit(0);
}
process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
