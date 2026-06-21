import asyncio
import sys
import time

import cv2
import numpy as np

from .detector import (
    decode_frame,
    detect_object,
    parse_description,
    FRAME_WIDTH,
    FRAME_HEIGHT,
)
from .vision import ask_llm_if_object_visible

MOVE_DELAY_SECONDS = 2
FOV_HORIZONTAL = 100
CENTER_THRESHOLD_PX = 64
MAX_CENTER_ATTEMPTS = 5
MAX_APPROACH_STEPS = 10
MAX_RESCANS = 2
MIN_SAFE_DISTANCE_CM = 20
TARGET_DISTANCE_CM = 50
CAMERA_TIMEOUT = 5.0
SCAN_STEP_DEGREES = 45
SCAN_STEPS = 8
STAR_STEP_DEGREES = 45
STAR_STEPS = 8
STAR_OFFSET_HALF_CM = 50
STAR_OFFSET_CM = 100
OPENCV_RETRY_FORWARD_1 = 50
OPENCV_RETRY_FORWARD_2 = 30


def _log(msg: str) -> None:
    print(f"[SEARCH_OBJECT] {msg}", file=sys.stderr, flush=True)


class SearchOrchestrator:

    def __init__(self, backend, *, llm_client, llm_model: str = "auto"):
        self._backend = backend
        self._llm_client = llm_client
        self._llm_model = llm_model
        self._steps_taken: list[str] = []
        self._last_bbox: tuple | None = None
        self._rescan_count = 0
        self._original_description: str = ""
        self._object_type: str = "cubo"
        self._object_color: str | None = None


    async def run(self, description: str) -> dict:
        t0 = time.monotonic()

        self._original_description = description
        self._object_type, self._object_color = parse_description(description)

        _log(f"=== INICIANDO BUSCA: type={self._object_type} color={self._object_color} desc='{description}' ===")

        _log("[FASE 1] Varredura 360 graus (scan 8x45)")
        scan_result = await self._scan(self._object_type, self._object_color)

        if scan_result is None:
            _log(f"[FASE 2] Scan nao encontrou. Iniciando exploracao em estrela 8x{STAR_STEP_DEGREES}graus com {STAR_OFFSET_HALF_CM}cm (star_explore)")
            scan_result = await self._star_explore(
                self._object_type, self._object_color, offset_cm=STAR_OFFSET_HALF_CM
            )

        if scan_result is None:
            _log(f"[FASE 2B] Star explore {STAR_OFFSET_HALF_CM}cm nao encontrou. Iniciando exploracao em estrela 8x{STAR_STEP_DEGREES}graus com {STAR_OFFSET_CM}cm (star_explore)")
            scan_result = await self._star_explore(
                self._object_type, self._object_color
            )

        if scan_result is None:
            _log("[RESULTADO] OBJETO NAO ENCONTRADO apos todas as tentativas")
            return {
                "status": "not_found",
                "object_type": self._object_type,
                "object_color": self._object_color,
                "bounding_box": None,
                "final_distance_cm": None,
                "steps_taken": self._steps_taken,
            }

        obj = scan_result["object"]
        self._last_bbox = obj["bbox"]
        _log(f"[FASE 3] Objeto detectado! bbox={obj['bbox']} center={obj['center']}. Iniciando centralizacao (center)")

        centered = await self._center(obj["center"])
        if not centered:
            _log("[RESULTADO] NAO FOI POSSIVEL CENTRALIZAR o objeto")
            return {
                "status": "not_found",
                "reason": "could not center",
                "object_type": self._object_type,
                "object_color": self._object_color,
                "bounding_box": self._last_bbox,
                "final_distance_cm": None,
                "steps_taken": self._steps_taken,
            }

        _log("[FASE 4] Objeto centralizado. Iniciando aproximacao (approach)")
        approach_result = await self._approach(self._object_type, self._object_color)

        elapsed = round(time.monotonic() - t0, 2)
        _log(f"[RESULTADO] status={approach_result.get('status')} distance={approach_result.get('final_distance_cm')} elapsed={elapsed}s steps={len(self._steps_taken)}")
        return {
            "status": approach_result.get("status", "not_found"),
            "reason": approach_result.get("reason"),
            "object_type": self._object_type,
            "object_color": self._object_color,
            "bounding_box": self._last_bbox,
            "final_distance_cm": approach_result.get("final_distance_cm"),
            "steps_taken": self._steps_taken,
            "elapsed_seconds": elapsed,
        }

    async def _scan(
        self, object_type: str, object_color: str | None
    ) -> dict | None:
        for i in range(SCAN_STEPS):
            angle = i * SCAN_STEP_DEGREES
            self._steps_taken.append(f"scan_frame_{i}")
            _log(f"  [scan {i}/{SCAN_STEPS}] Tirando foto na orientacao {angle} graus")

            try:
                camera_data = await asyncio.wait_for(
                    self._backend.get_camera(), timeout=CAMERA_TIMEOUT
                )
            except asyncio.TimeoutError:
                self._steps_taken.append("camera_timeout")
                _log(f"  [scan {i}/{SCAN_STEPS}] TIMEOUT da camera, pulando")
                continue
            except Exception:
                self._steps_taken.append("camera_error")
                _log(f"  [scan {i}/{SCAN_STEPS}] ERRO da camera, pulando")
                continue

            image_base64 = camera_data["image"]
            frame = decode_frame(image_base64)

            if frame is None or frame.shape[0] == 0:
                _log(f"  [scan {i}/{SCAN_STEPS}] Frame vazio, pulando")
                continue

            llm_description = self._original_description
            if not llm_description:
                llm_description = f"{object_color} {object_type}" if object_color else object_type

            _log(f"  [scan {i}/{SCAN_STEPS}] Perguntando para LLM se '{llm_description}' esta visivel...")
            llm_sees = await ask_llm_if_object_visible(
                self._llm_client, self._llm_model,
                image_base64, llm_description,
            )

            if not llm_sees:
                self._steps_taken.append(f"llm_not_found_at_{angle}deg")
                _log(f"  [scan {i}/{SCAN_STEPS}] LLM: NAO VIU objeto em {angle} graus")
                if i < SCAN_STEPS - 1:
                    _log(f"  [scan {i}/{SCAN_STEPS}] Girando -{SCAN_STEP_DEGREES} graus (esquerda)")
                    await self._rotate(-SCAN_STEP_DEGREES)
                continue

            self._steps_taken.append(f"llm_detected_at_{angle}deg")
            _log(f"  [scan {i}/{SCAN_STEPS}] LLM: AVISTOU objeto em {angle} graus! Confirmando com OpenCV...")
            result = detect_object(frame, object_type, object_color)

            if result is not None:
                self._steps_taken.append(f"cv_confirmed_at_{angle}deg")
                _log(f"  [scan {i}/{SCAN_STEPS}] OpenCV: CONFIRMOU deteccao em {angle} graus. bbox={result['bbox']}")
                return {"object": result, "angle": angle}

            self._steps_taken.append(f"cv_not_confirmed_at_{angle}deg")
            _log(f"  [scan {i}/{SCAN_STEPS}] OpenCV: NAO CONFIRMOU, continuando")
            if i < SCAN_STEPS - 1:
                _log(f"  [scan {i}/{SCAN_STEPS}] Girando -{SCAN_STEP_DEGREES} graus (esquerda)")
                await self._rotate(-SCAN_STEP_DEGREES)

        _log(f"  [scan] Fim da varredura 360 ({SCAN_STEPS}x{SCAN_STEP_DEGREES}graus)")
        return None

    async def _capture_frame(self) -> np.ndarray | None:
        try:
            camera_data = await asyncio.wait_for(
                self._backend.get_camera(), timeout=CAMERA_TIMEOUT
            )
            return decode_frame(camera_data["image"])
        except asyncio.TimeoutError:
            self._steps_taken.append("camera_timeout")
            _log("  [capture] TIMEOUT da camera")
            return None
        except Exception:
            self._steps_taken.append("camera_error")
            _log("  [capture] ERRO da camera")
            return None

    async def _rotate(self, degrees: float) -> None:
        direction = "R" if degrees > 0 else "L"
        cmd = f"R{int(abs(degrees))}{direction};"
        _log(f"  [movimento] Rotacionando {int(abs(degrees))} graus para {'direita' if direction == 'R' else 'esquerda'} ({cmd})")
        await self._backend.execute_lbml(cmd)
        self._steps_taken.append(f"rotate_{cmd.strip(';')}")
        await asyncio.sleep(MOVE_DELAY_SECONDS)

    async def _move_forward(self, cm: int) -> None:
        cmd = f"D{cm}F;"
        _log(f"  [movimento] Avancando {cm}cm para frente ({cmd})")
        await self._backend.execute_lbml(cmd)
        self._steps_taken.append(f"forward_{cm}cm")
        await asyncio.sleep(MOVE_DELAY_SECONDS)

    async def _move_backward(self, cm: int) -> None:
        cmd = f"D{cm}B;"
        _log(f"  [movimento] Recuando {cm}cm para tras ({cmd})")
        await self._backend.execute_lbml(cmd)
        self._steps_taken.append(f"backward_{cm}cm")
        await asyncio.sleep(MOVE_DELAY_SECONDS)

    async def _star_explore(
        self, object_type: str, object_color: str | None, offset_cm: int = STAR_OFFSET_CM
    ) -> dict | None:
        _log(f"  [star {offset_cm}cm] Iniciando exploracao em estrela: {STAR_STEPS}x{STAR_STEP_DEGREES}graus, offset={offset_cm}cm")
        self._steps_taken.append(f"star_explore_{offset_cm}cm_start")

        for direction in range(STAR_STEPS):
            self._steps_taken.append(f"star_explore_{offset_cm}cm_direction_{direction}")
            _log(f"  [star {offset_cm}cm {direction}/{STAR_STEPS}] Girando {STAR_STEP_DEGREES} graus para nova direcao")
            await self._rotate(STAR_STEP_DEGREES)

            try:
                sensor_data = await asyncio.wait_for(
                    self._backend.get_proximity_sensor(), timeout=CAMERA_TIMEOUT
                )
                distance_frente = sensor_data.get("frente", 999)
            except (asyncio.TimeoutError, Exception):
                _log(f"  [star {offset_cm}cm {direction}/{STAR_STEPS}] Sensor indisponivel, assumindo caminho livre")
                distance_frente = 999

            safe_advance = min(offset_cm, max(0, distance_frente - MIN_SAFE_DISTANCE_CM))
            if safe_advance <= 0:
                _log(f"  [star {offset_cm}cm {direction}/{STAR_STEPS}] Obstaculo muito perto (sensor={distance_frente:.0f}cm), pulando direcao")
                await self._rotate(-STAR_STEP_DEGREES)
                continue

            if safe_advance < offset_cm:
                _log(f"  [star {offset_cm}cm {direction}/{STAR_STEPS}] Obstaculo a {distance_frente:.0f}cm, avancando apenas {safe_advance}cm (seguro)")
            else:
                _log(f"  [star {offset_cm}cm {direction}/{STAR_STEPS}] Avancando {safe_advance}cm")

            await self._move_forward(safe_advance)

            frame = await self._capture_frame()
            if frame is None:
                _log(f"  [star {offset_cm}cm {direction}/{STAR_STEPS}] Frame vazio, recuando")
                await self._move_backward(safe_advance)
                continue

            camera_data = await asyncio.wait_for(
                self._backend.get_camera(), timeout=CAMERA_TIMEOUT
            )
            image_base64 = camera_data["image"]

            llm_description = self._original_description
            if not llm_description:
                llm_description = f"{object_color} {object_type}" if object_color else object_type

            _log(f"  [star {offset_cm}cm {direction}/{STAR_STEPS}] Perguntando para LLM...")
            llm_sees = await ask_llm_if_object_visible(
                self._llm_client, self._llm_model,
                image_base64, llm_description,
            )

            if not llm_sees:
                self._steps_taken.append(f"star_{offset_cm}cm_dir_{direction}_llm_not_found")
                _log(f"  [star {offset_cm}cm {direction}/{STAR_STEPS}] LLM: NAO VIU. Recuando {safe_advance}cm")
                await self._move_backward(safe_advance)
                continue

            self._steps_taken.append(f"star_{offset_cm}cm_dir_{direction}_llm_detected")
            _log(f"  [star {offset_cm}cm {direction}/{STAR_STEPS}] LLM: AVISTOU! Confirmando com OpenCV...")
            result = detect_object(frame, object_type, object_color)

            if result is not None:
                self._steps_taken.append(f"star_{offset_cm}cm_cv_confirmed_dir_{direction}")
                _log(f"  [star {offset_cm}cm {direction}/{STAR_STEPS}] OpenCV: CONFIRMOU! bbox={result['bbox']}")
                return {"object": result, "angle": direction * STAR_STEP_DEGREES}

            self._steps_taken.append(f"star_{offset_cm}cm_cv_not_confirmed_dir_{direction}")
            _log(f"  [star {offset_cm}cm {direction}/{STAR_STEPS}] OpenCV: NAO CONFIRMOU. Recuando {safe_advance}cm")
            await self._move_backward(safe_advance)

        _log(f"  [star {offset_cm}cm] Fim da exploracao em estrela. Nada encontrado")
        return None

    async def _retry_detect_with_advance(self) -> dict | None:
        _log("  [retry_detect] Avancando 50cm para tentar detectar...")
        self._steps_taken.append("retry_detect_forward_50cm")
        await self._move_forward(OPENCV_RETRY_FORWARD_1)
        frame = await self._capture_frame()
        if frame is not None:
            result = detect_object(frame, self._object_type, self._object_color)
            if result is not None:
                _log(f"  [retry_detect] DETECTOU apos 50cm! bbox={result['bbox']}")
                return result
            _log("  [retry_detect] Nao detectou apos 50cm")

        _log("  [retry_detect] Avancando mais 30cm...")
        self._steps_taken.append("retry_detect_forward_30cm")
        await self._move_forward(OPENCV_RETRY_FORWARD_2)
        frame = await self._capture_frame()
        if frame is not None:
            result = detect_object(frame, self._object_type, self._object_color)
            if result is not None:
                _log(f"  [retry_detect] DETECTOU apos +30cm! bbox={result['bbox']}")
                return result
            _log("  [retry_detect] Nao detectou apos +30cm")

        _log("  [retry_detect] Fim. Nao encontrou")
        return None

    async def _center(self, object_center: tuple[int, int]) -> bool:
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

            result = detect_object(frame, self._object_type, self._object_color)
            if result is None:
                _log(f"  [center] PERDEU TRACKING! Tentando recuperar com avanco (50cm + 30cm)...")
                result = await self._retry_detect_with_advance()
                if result is None:
                    _log(f"  [center] NAO RECUPEROU tracking apos avanco")
                    return False
                cx, cy = result["center"]
                self._last_bbox = result["bbox"]
                _log(f"  [center] RECUPEROU tracking! Novo centro=({cx},{cy})")
                continue

            cx, cy = result["center"]
            self._last_bbox = result["bbox"]
            _log(f"  [center] Re-detectado em ({cx},{cy}) bbox={result['bbox']}")

        _log(f"  [center] Maximo de tentativas ({MAX_CENTER_ATTEMPTS}) excedido")
        return False

    async def _approach(self, object_type: str, object_color: str | None) -> dict:
        step_count = 0
        rescan_count = 0
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
                _log(f"  [approach] Distancia alvo atingida ({distance:.0f}cm <= {TARGET_DISTANCE_CM}cm). Confirmando com camera...")
                self._steps_taken.append("approach_target_reached_confirming")
                confirmed = await self._confirm_via_camera()
                if confirmed:
                    self._steps_taken.append("camera_confirmed_object")
                    _log("  [approach] Camera CONFIRMOU o objeto! Busca concluida com sucesso")
                    return {"status": "found", "final_distance_cm": distance}
                self._steps_taken.append("camera_did_not_confirm")
                _log("  [approach] Camera NAO CONFIRMOU o objeto")
                return {"status": "not_found", "reason": "camera did not confirm object"}

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
                _log(f"  [approach] OpenCV PERDEU TRACKING! Tentando rescan ({rescan_count + 1}/{MAX_RESCANS})")
                self._steps_taken.append("tracking_lost_rescan")
                if rescan_count >= MAX_RESCANS:
                    return {"status": "not_found", "reason": "lost tracking after rescan"}
                rescan_count += 1
                scan_result = await self._scan(object_type, object_color)
                if scan_result is None:
                    return {"status": "not_found", "reason": "lost tracking after rescan"}
                obj = scan_result["object"]
                cx, cy = obj["center"]
                self._last_bbox = obj["bbox"]
                _log(f"  [approach] Rescan SUCESSO! Objeto re-encontrado em ({cx},{cy})")
            else:
                cx, cy = result["center"]
                self._last_bbox = result["bbox"]
                _log(f"  [approach] OpenCV detectou em ({cx},{cy}) bbox={result['bbox']}")

            _log(f"  [approach] Recentralizando apos movimento (obrigatorio)...")
            centered = await self._center((cx, cy))
            if not centered:
                _log(f"  [approach] FALHA na recentralizacao! Tentando rescan ({rescan_count + 1}/{MAX_RESCANS})")
                self._steps_taken.append("recenter_failed")
                if rescan_count >= MAX_RESCANS:
                    return {"status": "not_found", "reason": "lost tracking after rescan"}
                rescan_count += 1
                scan_result = await self._scan(object_type, object_color)
                if scan_result is None:
                    return {"status": "not_found", "reason": "lost tracking after rescan"}
                obj = scan_result["object"]
                self._last_bbox = obj["bbox"]
                _log(f"  [approach] Rescan SUCESSO! Objeto re-encontrado apos falha de center. bbox={obj['bbox']}")

        _log(f"  [approach] Maximo de passos ({MAX_APPROACH_STEPS}) excedido")
        return {"status": "not_found", "reason": "max approach steps exceeded"}

    async def _confirm_via_camera(self) -> bool:
        self._steps_taken.append("camera_confirmation_check")
        _log("  [confirm] Verificando se camera ve o objeto...")
        try:
            camera_data = await asyncio.wait_for(
                self._backend.get_camera(), timeout=CAMERA_TIMEOUT
            )
            image_base64 = camera_data["image"]
        except (asyncio.TimeoutError, Exception):
            self._steps_taken.append("camera_confirmation_error")
            _log("  [confirm] ERRO ao capturar camera")
            return False

        llm_description = self._original_description
        if not llm_description:
            llm_description = (
                f"{self._object_color} {self._object_type}"
                if self._object_color else self._object_type
            )

        result = await ask_llm_if_object_visible(
            self._llm_client, self._llm_model,
            image_base64, llm_description,
        )
        _log(f"  [confirm] LLM: {'SIM' if result else 'NAO'}")
        return result
