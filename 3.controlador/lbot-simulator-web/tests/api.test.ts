import { spawn, type ChildProcess } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, it, expect, beforeAll, afterAll } from 'vitest';

let BASE_URL: string;
let serverProcess: ChildProcess;

const __dirname = dirname(fileURLToPath(import.meta.url));
const TSC_PATH = resolve(__dirname, '..', 'node_modules', '.bin', 'tsx');

beforeAll(async () => {
  const port = Math.floor(Math.random() * 10000) + 20000;
  const serverDir = resolve(__dirname, '..');

  await new Promise<void>((resolve, reject) => {
    serverProcess = spawn(TSC_PATH, ['server/index.ts'], {
      cwd: serverDir,
      env: { ...process.env, PORT: String(port), NODE_ENV: 'test' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    const timeout = setTimeout(() => {
      reject(new Error('Server startup timeout'));
    }, 30000);

    let startupOutput = '';

    serverProcess.stdout?.on('data', (data: Buffer) => {
      startupOutput += data.toString();
      if (startupOutput.includes('listening')) {
        clearTimeout(timeout);
        BASE_URL = `http://localhost:${port}`;
        resolve();
      }
    });

    serverProcess.stderr?.on('data', (data: Buffer) => {
      startupOutput += data.toString();
      if (startupOutput.includes('listening')) {
        clearTimeout(timeout);
        BASE_URL = `http://localhost:${port}`;
        resolve();
      }
    });

    serverProcess.on('error', (err) => {
      clearTimeout(timeout);
      reject(err);
    });
  });
}, 45000);

afterAll(() => {
  if (serverProcess) {
    serverProcess.kill('SIGTERM');
  }
});

describe('/api/health', () => {
  it('returns online status', async () => {
    const response = await fetch(`${BASE_URL}/api/health`);
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.status).toBe('online');
  });
});

describe('/api/camera', () => {
  it('returns 200 with image base64 data', async () => {
    const response = await fetch(`${BASE_URL}/api/camera`);
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('image');
    expect(typeof data.image).toBe('string');
    expect(data.image!.length).toBeGreaterThan(0);
    expect(data.format).toBe('png');
    expect(data.encoding).toBe('base64');
  });

  it('returns connected=true when working', async () => {
    const response = await fetch(`${BASE_URL}/api/camera`);
    const data = await response.json();
    expect(data.connected).toBe(true);
  });

  it('returns robotPosition with coordinates', async () => {
    const response = await fetch(`${BASE_URL}/api/camera`);
    const data = await response.json();
    expect(data.robotPosition).toBeDefined();
  });

  it('works without browser (headless)', async () => {
    const response = await fetch(`${BASE_URL}/api/camera`);
    expect(response.status).toBe(200);
  });

  it('base64 string is valid PNG (starts with iVBOR)', async () => {
    const response = await fetch(`${BASE_URL}/api/camera`);
    const data = await response.json();
    const base64Prefix = 'iVBOR';
    expect(data.image!.startsWith(base64Prefix)).toBe(true);
  });
});

describe('/api/sensors', () => {
  it('returns 200 with readings', async () => {
    const response = await fetch(`${BASE_URL}/api/sensors`);
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.readings).toBeDefined();
  });

  it('returns connected=true', async () => {
    const response = await fetch(`${BASE_URL}/api/sensors`);
    const data = await response.json();
    expect(data.connected).toBe(true);
  });

  it('returns frente and tras as numbers', async () => {
    const response = await fetch(`${BASE_URL}/api/sensors`);
    const data = await response.json();
    expect(typeof data.readings.frente).toBe('number');
    expect(typeof data.readings.tras).toBe('number');
  });

  it('center position returns approximately 200cm (frente/tras)', async () => {
    const response = await fetch(`${BASE_URL}/api/sensors`);
    const data = await response.json();
    expect(data.readings.frente).toBeGreaterThan(0);
    expect(data.readings.frente).toBeLessThanOrEqual(400);
    expect(data.readings.tras).toBeGreaterThan(0);
    expect(data.readings.tras).toBeLessThanOrEqual(400);
  });

  it('works without browser (headless)', async () => {
    const response = await fetch(`${BASE_URL}/api/sensors`);
    expect(response.status).toBe(200);
  });
});

describe('/api/status', () => {
  it('returns connected status without browser', async () => {
    const response = await fetch(`${BASE_URL}/api/status`);
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('connected');
    expect(data.connected).toBe(false);
  });
});

describe('/api/state', () => {
  it('returns null state without active browser', async () => {
    const response = await fetch(`${BASE_URL}/api/state`);
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.state).toBeNull();
  });
});
