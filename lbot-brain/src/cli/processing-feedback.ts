import { spawn, type ChildProcess } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { stdout } from "node:process";

const SPINNER_FRAMES = ["|", "/", "-", "\\"];
const SPINNER_INTERVAL_MS = 120;
const PROCESSING_SOUND_PATH = path.resolve(__dirname, "..", "..", "assets", "sounds", "processing-loop.wav");

function isInteractiveTerminal(): boolean {
  return Boolean(stdout.isTTY);
}

function clearLine(): void {
  if (!isInteractiveTerminal()) {
    return;
  }

  stdout.write("\r\x1b[2K");
}

function startSpinner(message: string): () => void {
  if (!isInteractiveTerminal()) {
    return () => undefined;
  }

  let frameIndex = 0;
  const render = () => {
    const frame = SPINNER_FRAMES[frameIndex % SPINNER_FRAMES.length];
    frameIndex += 1;
    stdout.write(`\r\x1b[2K${frame} ${message}`);
  };

  render();
  const timer = setInterval(render, SPINNER_INTERVAL_MS);

  return () => {
    clearInterval(timer);
    clearLine();
  };
}

function startSoundLoop(): () => void {
  if (!existsSync(PROCESSING_SOUND_PATH)) {
    return () => undefined;
  }

  const loopScript = `while true; do afplay "${PROCESSING_SOUND_PATH}"; done`;
  const child = spawn("/bin/sh", ["-c", loopScript], {
    stdio: "ignore",
  });

  const stopChild = () => {
    if (child.exitCode === null && !child.killed) {
      child.kill("SIGTERM");
    }
  };

  child.on("error", stopChild);

  return stopChild;
}

export interface ProcessingFeedback {
  start(message: string): () => void;
}

export function createProcessingFeedback(): ProcessingFeedback {
  return {
    start(message: string): () => void {
      const stopSpinner = startSpinner(message);
      const stopSound = startSoundLoop();
      let stopped = false;

      return () => {
        if (stopped) {
          return;
        }

        stopped = true;
        stopSound();
        stopSpinner();
      };
    },
  };
}
