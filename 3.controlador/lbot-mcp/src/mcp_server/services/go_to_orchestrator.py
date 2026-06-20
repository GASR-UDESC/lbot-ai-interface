import asyncio
import sys

import cv2
import numpy as np

from .detector import (
    decode_frame,
    detect_object,
    parse_description,
    FRAME_WIDTH,
    FRAME_HEIGHT,
)
from ..lbml import move_duration_s, rotate_duration_s
from .vision import ask_llm_if_object_visible
FOV_HORIZONTAL = 100
CENTER_THRESHOLD_PX = 64
MAX_CENTER_ATTEMPTS = 5
MAX_APPROACH_STEPS = 10
MIN_SAFE_DISTANCE_CM = 20
TARGET_DISTANCE_CM = 50
WALL_STOP_DISTANCE_CM = 20
CAMERA_TIMEOUT = 5.0

DIRECTION_ANGLES: dict[str, int] = {
    "frente": 0,
    "esquerda": -90,
    "direita": 90,
    "tras": 180,
}

WALL_KEYWORDS = {"parede", "muro", "paredes", "muros"}


def _log(msg: str) -> None:
    print(f"[GO_TO] {msg}", file=sys.stderr, flush=True)


class GoToOrchestrator:

    def __init__(self, backend, *, llm_client, llm_model: str = "auto"):
        self._backend = backend
        self._llm_client = llm_client
        self._llm_model = llm_model
        self._steps_taken: list[str] = []
        self._last_bbox: tuple | None = None

    async def run(self, target: str, direction: str) -> dict:
        direction = direction.lower().strip()
        if direction not in DIRECTION_ANGLES:
            return {
                "status": "error",
                "error": f"direcao invalida: '{direction}'. Use: frente, esquerda, direita, tras",
            }

        target = target.strip()
        if not target:
            return {
                "status": "error",
                "error": "alvo nao pode ser vazio",
            }

        is_wall = self._is_wall_target(target)
        is_object = not is_wall and self._is_object_target(target)

        if not is_wall and not is_object:
            return {
                "status": "error",
                "error": f"alvo nao reconhecido: '{target}'. Use 'parede', 'cubo vermelho', 'esfera azul', etc.",
            }

        degrees = DIRECTION_ANGLES[direction]
        _log(f"=== INICIANDO GO_TO: target='{target}' direction='{direction}' degrees={degrees} is_wall={is_wall} ===")

        if degrees != 0:
            _log(f"Girando {abs(degrees)} graus para '{direction}'")
            await self._rotate(degrees)

        camera_data = await self._capture_camera_data()
        if camera_data is None:
            return {
                "status": "error",
                "error": "camera indisponivel",
            }

        image_base64 = camera_data["image"]

        _log(f"Perguntando ao LLM se '{target}' esta visivel...")
        llm_sees = await ask_llm_if_object_visible(
            self._llm_client, self._llm_model,
            image_base64, target,
        )

        if not llm_sees:
            self._steps_taken.append("llm_did_not_confirm")
            _log(f"LLM: NAO VIU '{target}' na direcao '{direction}'")
            return {
                "status": "not_found",
                "reason": "target not visible in direction",
                "target": target,
                "direction": direction,
                "steps_taken": self._steps_taken,
            }

        self._steps_taken.append("llm_confirmed")
        _log(f"LLM: CONFIRMOU '{target}' na direcao '{direction}'")

        if is_wall:
            return await self._approach_wall(target, direction)
        else:
            return await self._go_to_object(target, direction, image_base64)

    def _is_wall_target(self, target: str) -> bool:
        return any(kw in target.lower() for kw in WALL_KEYWORDS)

    def _is_object_target(self, target: str) -> bool:
        text = target.lower()
        type_keywords = {"cubo", "cubos", "esfera", "esferas", "bola", "bolas", "cone", "cones"}
        if any(kw in text for kw in type_keywords):
            return True
        from .detector import COLOR_RANGES
        if any(color in text for color in COLOR_RANGES):
            return True
        return False

    async def _capture_camera_data(self) -> dict | None:
        try:
            return await asyncio.wait_for(
                self._backend.get_camera(), timeout=CAMERA_TIMEOUT
            )
        except asyncio.TimeoutError:
            self._steps_taken.append("camera_timeout")
            _log("[capture] TIMEOUT da camera")
            return None
        except Exception:
            self._steps_taken.append("camera_error")
            _log("[capture] ERRO da camera")
            return None

    async def _capture_frame(self) -> np.ndarray | None:
        camera_data = await self._capture_camera_data()
        if camera_data is None:
            return None
        return decode_frame(camera_data["image"])

    async def _rotate(self, degrees: float) -> None:
        direction = "R" if degrees > 0 else "L"
        cmd = f"R{int(abs(degrees))}{direction};"
        _log(f"  [movimento] Rotacionando {int(abs(degrees))} graus para {'direita' if direction == 'R' else 'esquerda'} ({cmd})")
        await self._backend.execute_lbml(cmd)
        self._steps_taken.append(f"rotate_{cmd.strip(';')}")
        await asyncio.sleep(rotate_duration_s(abs(degrees)))

    async def _move_forward(self, cm: int) -> None:
        cmd = f"D{cm}F;"
        _log(f"  [movimento] Avancando {cm}cm para frente ({cmd})")
        await self._backend.execute_lbml(cmd)
        self._steps_taken.append(f"forward_{cm}cm")
        await asyncio.sleep(move_duration_s(cm))

    async def _get_front_sensor(self) -> float | None:
        try:
            sensor = await asyncio.wait_for(
                self._backend.get_proximity_sensor(), timeout=CAMERA_TIMEOUT
            )
            return float(sensor["frente"])
        except asyncio.TimeoutError:
            self._steps_taken.append("sensor_timeout")
            _log("[sensor] TIMEOUT")
            return None
        except Exception:
            self._steps_taken.append("sensor_error")
            _log("[sensor] ERRO")
            return None

    async def _approach_wall(self, target: str, direction: str) -> dict:
        _log("[approach_wall] Iniciando aproximacao ate parede")
        self._steps_taken.append("approach_wall_start")

        distance = await self._get_front_sensor()
        if distance is None:
            return {
                "status": "error",
                "error": "sensor de proximidade indisponivel",
                "target": target,
                "direction": direction,
                "steps_taken": self._steps_taken,
            }

        self._steps_taken.append(f"sensor_read_{distance:.0f}cm")
        _log(f"[approach_wall] Sensor frontal: {distance:.0f}cm")

        if distance < WALL_STOP_DISTANCE_CM:
            _log(f"[approach_wall] Ja esta a {distance:.0f}cm da parede (limite={WALL_STOP_DISTANCE_CM}cm)")
            return {
                "status": "found",
                "target": target,
                "direction": direction,
                "final_distance_cm": distance,
                "steps_taken": self._steps_taken,
            }

        if distance >= 400:
            self._steps_taken.append("wall_no_obstacle")
            _log(f"[approach_wall] Sem obstaculo detectado (>400cm)")
            return {
                "status": "not_found",
                "reason": "no obstacle detected",
                "target": target,
                "direction": direction,
                "steps_taken": self._steps_taken,
            }

        advance = max(1, int(distance - WALL_STOP_DISTANCE_CM))
        _log(f"[approach_wall] Avancando {advance}cm ({distance:.0f} - {WALL_STOP_DISTANCE_CM})")
        await self._move_forward(advance)
        self._steps_taken.append(f"wall_advance_{advance}cm")

        final_distance = await self._get_front_sensor()
        final_str = f"{final_distance:.0f}cm" if final_distance is not None else "desconhecida"
        _log(f"[approach_wall] Distancia final: {final_str}")
        self._steps_taken.append(f"wall_arrived_{final_str}")

        return {
            "status": "found",
            "target": target,
            "direction": direction,
            "final_distance_cm": final_distance,
            "steps_taken": self._steps_taken,
        }

    async def _go_to_object(self, target: str, direction: str, image_base64: str) -> dict:
        frame = decode_frame(image_base64)
        object_type, object_color = parse_description(target)
        _log(f"[go_to_object] object_type={object_type} object_color={object_color}")

        result = detect_object(frame, object_type, object_color)
        if result is None:
            self._steps_taken.append("opencv_not_detected")
            _log("[go_to_object] OpenCV NAO DETECTOU objeto (LLM confirmou mas CV falhou)")
            return {
                "status": "not_found",
                "reason": "LLM confirmed but OpenCV could not detect",
                "target": target,
                "direction": direction,
                "object_type": object_type,
                "object_color": object_color,
                "steps_taken": self._steps_taken,
            }

        self._last_bbox = result["bbox"]
        self._steps_taken.append("opencv_detected")
        _log(f"[go_to_object] OpenCV DETECTOU: bbox={result['bbox']} center={result['center']}")

        centered = await self._center(result["center"], object_type, object_color)
        if not centered:
            _log("[go_to_object] NAO FOI POSSIVEL CENTRALIZAR o objeto")
            return {
                "status": "not_found",
                "reason": "could not center",
                "target": target,
                "direction": direction,
                "object_type": object_type,
                "object_color": object_color,
                "bounding_box": self._last_bbox,
                "steps_taken": self._steps_taken,
            }

        _log("[go_to_object] Objeto centralizado. Iniciando aproximacao")
        approach_result = await self._approach_object(object_type, object_color)

        return {
            "status": approach_result.get("status", "not_found"),
            "reason": approach_result.get("reason"),
            "target": target,
            "direction": direction,
            "object_type": object_type,
            "object_color": object_color,
            "bounding_box": self._last_bbox,
            "final_distance_cm": approach_result.get("final_distance_cm"),
            "steps_taken": self._steps_taken,
        }

    async def _center(
        self, object_center: tuple[int, int], object_type: str, object_color: str | None
    ) -> bool:
        cx, cy = object_center
        _log(f"  [center] Iniciando centralizacao. centro=({cx},{cy}) frame_center=({FRAME_WIDTH/2},{FRAME_HEIGHT/2})")

        for attempt in range(MAX_CENTER_ATTEMPTS):
            erro_x = cx - FRAME_WIDTH / 2

            if abs(erro_x) < CENTER_THRESHOLD_PX:
                self._steps_taken.append(f"centered_attempt_{attempt + 1}")
                _log(f"  [center] OK! Objeto centralizado na tentativa {attempt + 1}. erro_x={erro_x:.0f}px (threshold={CENTER_THRESHOLD_PX}px)")
                return True

            graus = (erro_x / FRAME_WIDTH) * FOV_HORIZONTAL
            _log(f"  [center] Tentativa {attempt + 1}/{MAX_CENTER_ATTEMPTS}: erro_x={erro_x:.0f}px = {graus:.1f} graus de ajuste")

            if abs(graus) < 1:
                self._steps_taken.append(f"centered_attempt_{attempt + 1}")
                _log(f"  [center] OK! Ajuste < 1 grau, considerando centralizado")
                return True

            self._steps_taken.append(f"center_attempt_{attempt + 1}_error_{erro_x:.0f}px")
            await self._rotate(graus)

            frame = await self._capture_frame()
            if frame is None:
                _log(f"  [center] Frame vazio apos rotacao, tentando de novo")
                continue

            result = detect_object(frame, object_type, object_color)
            if result is None:
                _log(f"  [center] PERDEU TRACKING! Abortando centralizacao")
                self._steps_taken.append("center_lost_tracking")
                return False

            cx, cy = result["center"]
            self._last_bbox = result["bbox"]
            _log(f"  [center] Re-detectado em ({cx},{cy}) bbox={result['bbox']}")

        _log(f"  [center] Maximo de tentativas ({MAX_CENTER_ATTEMPTS}) excedido")
        return False

    async def _approach_object(self, object_type: str, object_color: str | None) -> dict:
        step_count = 0
        _log("  [approach] Iniciando aproximacao (passos de 1/3 da distancia, centralizando a cada passo)")

        while step_count < MAX_APPROACH_STEPS:
            sensor = await self._backend.get_proximity_sensor()
            distance = sensor["frente"]

            self._steps_taken.append(f"approach_step_{step_count + 1}_sensor_{distance:.0f}cm")
            _log(f"  [approach] Passo {step_count + 1}/{MAX_APPROACH_STEPS}: sensor_frente={distance:.0f}cm")

            if distance < MIN_SAFE_DISTANCE_CM:
                _log(f"  [approach] OBSTACULO MUITO PERTO! distancia={distance:.0f}cm < seguro={MIN_SAFE_DISTANCE_CM}cm")
                return {"status": "not_found", "reason": "obstacle too close"}

            if distance <= TARGET_DISTANCE_CM:
                _log(f"  [approach] Distancia alvo atingida ({distance:.0f}cm <= {TARGET_DISTANCE_CM}cm)")
                self._steps_taken.append("approach_target_reached")
                return {"status": "found", "final_distance_cm": distance}

            step = max(5, int(distance / 3))
            self._steps_taken.append(f"approach_step_{step}cm")
            _log(f"  [approach] Avancando {step}cm (1/3 de {distance:.0f}cm)")
            await self._move_forward(step)
            step_count += 1

            frame = await self._capture_frame()
            if frame is None:
                _log(f"  [approach] Frame vazio, pulando verificacao")
                continue

            result = detect_object(frame, object_type, object_color)

            if result is None:
                _log(f"  [approach] PERDEU TRACKING! Abortando aproximacao")
                self._steps_taken.append("tracking_lost")
                return {"status": "not_found", "reason": "lost tracking"}

            cx, cy = result["center"]
            self._last_bbox = result["bbox"]
            _log(f"  [approach] OpenCV detectou em ({cx},{cy}) bbox={result['bbox']}")

            _log(f"  [approach] Recentralizando apos movimento...")
            centered = await self._center((cx, cy), object_type, object_color)
            if not centered:
                _log(f"  [approach] FALHA na recentralizacao! Abortando")
                self._steps_taken.append("recenter_failed")
                return {"status": "not_found", "reason": "could not center after approach step"}

        _log(f"  [approach] Maximo de passos ({MAX_APPROACH_STEPS}) excedido")
        return {"status": "not_found", "reason": "max approach steps exceeded"}
