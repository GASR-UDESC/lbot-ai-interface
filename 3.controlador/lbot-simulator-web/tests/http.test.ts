import { test } from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { chromium } from "playwright";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
const port = 32000 + Math.floor(Math.random() * 1000),
  url = `http://127.0.0.1:${port}`;
const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));
test(
  "HTTP execution, cancellation and 3D camera work without a UI tab",
  { timeout: 60000 },
  async () => {
    const child = spawn(
      process.execPath,
      ["--import", "tsx", "server/index.ts"],
      {
        env: {
          ...process.env,
          PORT: String(port),
          NODE_ENV: "production",
          LBOT_ENABLE_EVAL: "1",
        },
        stdio: "pipe",
      },
    );
    let errors = "";
    child.stderr.on("data", (d) => {
      errors = (errors + String(d)).slice(-2000);
    });
    try {
      let online = false;
      for (let i = 0; i < 100; i++) {
        try {
          online = (await fetch(url + "/api/health")).ok;
        } catch {}
        if (online) break;
        await delay(100);
      }
      assert.ok(online, errors);
      const post = (path: string, body: unknown = {}) =>
        fetch(url + path, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
      const initial = (await (await fetch(url + "/api/state")).json()).state;
      assert.equal(
        (
          await post("/api/commands", {
            command: "D20F;",
            command_id: { invalid: true },
          })
        ).status,
        400,
      );
      assert.equal(
        (
          await post("/api/scenario", {
            objects: [
              {
                id: "bad",
                type: "cube",
                x: 0,
                z: 50,
                color: "#ff0000",
                size: {},
              },
            ],
          })
        ).status,
        400,
      );
      assert.equal(
        (await (await fetch(url + "/api/status")).json()).activeClientId,
        null,
      );
      const record = await (
        await post("/api/commands", {
          command: "D100F;",
          command_id: "duplicate",
        })
      ).json();
      assert.equal(record.status, "accepted");
      assert.equal(
        (
          await (
            await post("/api/commands", {
              command: "D100F;",
              command_id: "duplicate",
            })
          ).json()
        ).command_id,
        "duplicate",
      );
      assert.equal(
        (await post("/api/commands", { command: "D10F;" })).status,
        409,
      );
      await post("/api/stop");
      assert.equal(
        (await (await fetch(url + "/api/commands/duplicate")).json()).status,
        "cancelled",
      );
      const reset = await (await post("/api/reset")).json();
      assert.notEqual(reset.session_id, initial.session_id);
      assert.equal(
        (
          await post("/api/commands", {
            command: "D10F;",
            session_id: initial.session_id,
          })
        ).status,
        409,
      );
      const next = await (
        await post("/api/commands", { command: "D10F;" })
      ).json();
      let terminal;
      for (let i = 0; i < 100; i++) {
        terminal = await (
          await fetch(url + "/api/commands/" + next.command_id)
        ).json();
        if (terminal.status === "completed") break;
        await delay(30);
      }
      assert.equal(terminal.status, "completed");
      assert.ok(Math.abs(terminal.distance_cm - 10) < 1);
      const camera = await (await fetch(url + "/api/camera")).json();
      assert.equal(camera.renderMethod, "webgl");
      assert.equal(camera.session_id, reset.session_id);
      assert.ok(camera.revision >= terminal.revision);
      const png = Buffer.from(camera.image, "base64");
      assert.equal(png.readUInt32BE(16), 640);
      assert.equal(png.readUInt32BE(20), 480);
      assert.ok(!("robotPosition" in camera));
      const sensor = await (await fetch(url + "/api/sensors")).json();
      assert.equal(sensor.session_id, reset.session_id);
      assert.ok(Math.abs(sensor.readings.frente - 174.9) < 1);
      await post("/api/reset");
      const current = (await (await fetch(url + "/api/state")).json()).state;
      assert.equal(current.z, 0);
      const browser = await chromium.launch({
        headless: true,
        args: ["--enable-unsafe-swiftshader"],
      });
      try {
        const page = await browser.newPage();
        await page.goto(url);
        await page.waitForSelector("canvas");
        const movement = await (
          await post("/api/commands", { command: "D30F;" })
        ).json();
        const second = await browser.newPage();
        await second.goto(url);
        await page.close();
        await second.close();
        for (let i = 0; i < 100; i++) {
          terminal = await (
            await fetch(url + "/api/commands/" + movement.command_id)
          ).json();
          if (terminal.status === "completed") break;
          await delay(30);
        }
        assert.equal(terminal.status, "completed");
        assert.ok(Math.abs(terminal.distance_cm - 30) < 1);
      } finally {
        await browser.close();
      }
    } finally {
      child.kill("SIGTERM");
      await new Promise<void>((resolve) => {
        if (child.exitCode !== null) resolve();
        else child.once("exit", () => resolve());
      });
    }
  },
);

test(
  "missing Chromium returns camera_unavailable, never a replacement image",
  { timeout: 30000 },
  async () => {
    const cache = await mkdtemp(join(tmpdir(), "lbot-no-browser-"));
    const failureUrl = `http://127.0.0.1:${port + 1}`;
    const child = spawn(
      process.execPath,
      ["--import", "tsx", "server/index.ts"],
      {
        env: {
          ...process.env,
          PORT: String(port + 1),
          NODE_ENV: "production",
          PLAYWRIGHT_BROWSERS_PATH: cache,
        },
        stdio: "pipe",
      },
    );
    child.stdout.resume();
    child.stderr.resume();
    try {
      let online = false;
      for (let i = 0; i < 100; i++) {
        try {
          online = (await fetch(failureUrl + "/api/health")).ok;
        } catch {}
        if (online) break;
        await delay(50);
      }
      assert.ok(online);
      const response = await fetch(failureUrl + "/api/camera");
      assert.equal(response.status, 503);
      const data = await response.json();
      assert.equal(data.error, "camera_unavailable");
      assert.equal(data.image, null);
    } finally {
      child.kill("SIGTERM");
      await new Promise<void>((resolve) =>
        child.exitCode !== null
          ? resolve()
          : child.once("exit", () => resolve()),
      );
      await rm(cache, { recursive: true, force: true });
    }
  },
);
