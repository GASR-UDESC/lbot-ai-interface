const HALF_ARENA = 200;
const MAX_SENSOR_DISTANCE = 400;

function degToRad(degrees: number): number {
  return (degrees * Math.PI) / 180;
}

function rayWallDistance(
  ox: number,
  oz: number,
  dx: number,
  dz: number,
): number {
  let minDist = Infinity;

  if (dx > 0.0001) {
    const t = (HALF_ARENA - ox) / dx;
    if (t > 0 && t < minDist) minDist = t;
  } else if (dx < -0.0001) {
    const t = (-HALF_ARENA - ox) / dx;
    if (t > 0 && t < minDist) minDist = t;
  }

  if (dz > 0.0001) {
    const t = (HALF_ARENA - oz) / dz;
    if (t > 0 && t < minDist) minDist = t;
  } else if (dz < -0.0001) {
    const t = (-HALF_ARENA - oz) / dz;
    if (t > 0 && t < minDist) minDist = t;
  }

  return minDist;
}

export function computeProximity(
  x: number,
  z: number,
  rotationDeg: number,
): { frente: number; tras: number } {
  const rad = degToRad(rotationDeg);
  const frontDx = Math.sin(rad);
  const frontDz = Math.cos(rad);

  let frente = rayWallDistance(x, z, frontDx, frontDz);
  if (frente > MAX_SENSOR_DISTANCE) {
    frente = MAX_SENSOR_DISTANCE;
  }

  let tras = rayWallDistance(x, z, -frontDx, -frontDz);
  if (tras > MAX_SENSOR_DISTANCE) {
    tras = MAX_SENSOR_DISTANCE;
  }

  return { frente: Math.round(frente * 100) / 100, tras: Math.round(tras * 100) / 100 };
}
