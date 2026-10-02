import { test } from "node:test";
import assert from "node:assert/strict";
import { Simulation, TERMINAL } from "../server/engine.js";
function run(sim: Simulation, command: string) {
  const record = sim.submit({ command });
  for (
    let i = 0;
    i < 10000 && !TERMINAL.has(sim.getCommand(record.command_id)!.status);
    i++
  )
    sim.tick();
  return sim.getCommand(record.command_id)!;
}
test("measured forward, backward and rotation use centimetres/degrees", () => {
  const sim = new Simulation([]);
  assert.equal(run(sim, "D30F;").status, "completed");
  assert.ok(Math.abs(sim.snapshot().z - 30) < 1);
  run(sim, "D10B;");
  assert.ok(Math.abs(sim.snapshot().z - 20) < 1);
  run(sim, "R90L;D20F;");
  assert.ok(Math.abs(sim.snapshot().x - 20) < 1);
});
test("full rotation, negative rotation and sequences retain heading", () => {
  const sim = new Simulation([]);
  run(sim, "R360L;R180R;R90L;");
  assert.ok(Math.abs(sim.snapshot().rotation - 270) < 0.1);
  run(sim, "D20R;");
  assert.ok(Math.abs(sim.snapshot().rotation - 180) < 0.1);
  assert.ok(Math.abs(sim.snapshot().z + 20) < 1);
});
test("idempotency and busy prevent duplicate/concurrent motion", () => {
  const sim = new Simulation([]);
  const req = { command: "D30F;", command_id: "one" };
  sim.submit(req);
  sim.submit(req);
  assert.throws(() => sim.submit({ command: "D20F;" }), /busy/);
  assert.throws(() => sim.submit({ ...req, command: "D40F;" }), /id_conflict/);
  for (let i = 0; i < 200; i++) sim.tick();
  assert.equal(sim.getCommand("one")!.status, "completed");
  sim.submit(req);
  assert.ok(sim.snapshot().z < 31);
});
test("stop and reset resolve active commands and invalidate sessions", () => {
  const sim = new Simulation([]);
  const cmd = sim.submit({ command: "D100F;" });
  sim.tick();
  sim.stop();
  assert.equal(sim.getCommand(cmd.command_id)!.status, "cancelled");
  assert.equal(sim.snapshot().isAnimating, false);
  const z = sim.snapshot().z;
  for (let i = 0; i < 100; i++) sim.tick();
  assert.equal(sim.snapshot().z, z);
  const session = sim.session;
  sim.reset();
  assert.notEqual(sim.session, session);
  assert.equal(sim.snapshot().z, 0);
  assert.throws(
    () => sim.submit({ command: "D20F;", session_id: session }),
    /stale_session/,
  );
});
test("obstacle interrupts before requested distance and sensor shares geometry", () => {
  const sim = new Simulation([
    {
      id: "block",
      type: "cube",
      x: 0,
      z: 80,
      color: "#f00",
      size: { width: 30, height: 20, depth: 20 },
    },
  ]);
  assert.ok(Math.abs(sim.sensors().readings!.frente - 54.9) < 0.2);
  const result = run(sim, "D100F;");
  assert.equal(result.status, "blocked");
  assert.ok(result.distance_cm < 60);
  assert.equal(sim.snapshot().isAnimating, false);
});
test("invalid, zero and excessively large commands do not move", () => {
  const sim = new Simulation([]);
  for (const command of ["D0F;", "D99999F;", "R0L;", "banana"])
    assert.throws(() => sim.submit({ command }), /invalid_command/);
  assert.equal(sim.snapshot().z, 0);
});

test("rotation close to a wall is blocked and velocities are cleared", () => {
  const sim = new Simulation([]);
  assert.equal(run(sim, "D183F;").status, "completed");
  const rotation = run(sim, "R360L;");
  assert.equal(rotation.status, "blocked");
  assert.ok(rotation.rotation_degrees < 360);
  assert.equal(sim.body.velocity.length(), 0);
  assert.equal(sim.body.angularVelocity.length(), 0);
});
