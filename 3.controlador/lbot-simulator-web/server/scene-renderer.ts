import { ARENA_OBJECTS, type ArenaObject } from "../shared/arena-objects.js";
import { chromium, type Browser, type Page } from "playwright";
import type { SimulatorStateSnapshot } from "../shared/protocol.js";
export class HeadlessSceneRenderer {
  private browser: Browser | null = null;
  private page: Page | null = null;
  private pending: Promise<void> = Promise.resolve();
  private starting: Promise<void> | null = null;
  private ready = false;
  constructor(private url: string) {}
  async start() {
    if (this.ready) return;
    if (!this.starting)
      this.starting = this.launch()
        .catch(async (e) => {
          await this.close();
          throw e;
        })
        .finally(() => {
          this.starting = null;
        });
    return this.starting;
  }
  private async launch() {
    this.browser = await chromium.launch({
      headless: true,
      args: [
        "--use-gl=angle",
        "--use-angle=swiftshader",
        "--enable-unsafe-swiftshader",
      ],
    });
    this.page = await this.browser.newPage({
      viewport: { width: 640, height: 480 },
    });
    await this.page.goto(this.url, {
      waitUntil: "networkidle",
      timeout: 30000,
    });
    await this.page.waitForFunction(
      () =>
        typeof (window as unknown as { renderRobotFrame?: unknown })
          .renderRobotFrame === "function",
      null,
      { timeout: 10000 },
    );
    this.ready = true;
  }
  async render(
    state: SimulatorStateSnapshot,
    objects: ArenaObject[] = ARENA_OBJECTS,
  ): Promise<string> {
    let resolve!: () => void;
    const previous = this.pending;
    this.pending = new Promise<void>((r) => {
      resolve = r;
    });
    await previous;
    try {
      await this.start();
      return await this.page!.evaluate(
        ({ state, objects }) =>
          (
            window as unknown as {
              renderRobotFrame: (
                state: SimulatorStateSnapshot,
                objects: ArenaObject[],
              ) => string;
            }
          ).renderRobotFrame(state, objects),
        { state, objects },
      );
    } catch (e) {
      await this.close();
      throw e;
    } finally {
      resolve();
    }
  }
  async close() {
    this.ready = false;
    await this.browser?.close().catch(() => {});
    this.browser = null;
    this.page = null;
  }
}
