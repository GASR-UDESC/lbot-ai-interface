export const CAMERA = {
  width: 640,
  height: 480,
  verticalFov: 70,
  heightCm: 8,
  forwardCm: 12,
};
const focal =
  CAMERA.height / (2 * Math.tan((CAMERA.verticalFov * Math.PI) / 360));
export const INTRINSICS = {
  width: CAMERA.width,
  height: CAMERA.height,
  fx: focal,
  fy: focal,
  cx: CAMERA.width / 2,
  cy: CAMERA.height / 2,
};

// Sensor beam expressed in the camera optical frame (x right, y down, z forward).
export const RANGE_PROJECTION = {
  origin_cm: [0, 2, 3.1],
  direction: [0, 0, 1],
};
