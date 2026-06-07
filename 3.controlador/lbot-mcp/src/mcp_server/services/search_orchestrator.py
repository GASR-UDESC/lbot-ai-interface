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
EXPLORE_OFFSET_CM = 50
EXPLORE_OFFSET_CM_2 = 75
MAX_EXPLORE_DIRECTIONS = 4
OPENCV_RETRY_FORWARD_1 = 50
OPENCV_RETRY_FORWARD_2 = 30
TARGETED_SWEEP_ADVANCE_CM = 50
TARGETED_SWEEP_ANGLE = 45


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
        self._llm_spotted: bool = False
        self._llm_spotted_angle: int | None = None

    async def run(self, description: str) -> dict:
        t0 = time.monotonic()

        self._original_description = description
        self._object_type, self._object_color = parse_description(description)

        _log(f"=== INICIANDO BUSCA: type={self._object_type} color={self._object_color} desc='{description}' ===")

        _log("[FASE 1] Varredura 360 graus (scan)")
        scan_result = await self._scan(self._object_type, self._object_color)

        if scan_result is None and self._llm_spotted:
            _log("[FASE 1b] LLM avistou mas OpenCV nao confirmou. Iniciando varredura direcionada +-45graus (targeted_opencv_sweep)")
            scan_result = await self._targeted_opencv_sweep()

        if scan_result is None:
            _log("[FASE 1c] Ainda nao encontrou. Iniciando exploracao em cruz 50cm (explore_offsets)")
            scan_result = await self._explore_offsets(
                self._object_type, self._object_color
            )

        if scan_result is None:
            _log("[FASE 1d] Cruz 50cm nao encontrou. Iniciando exploracao em cruz 75cm (explore_offsets)")
            scan_result = await self._explore_offsets(
                self._object_type, self._object_color, offset=EXPLORE_OFFSET_CM_2
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
        _log(f"[FASE 2] Objeto detectado! bbox={obj['bbox']} center={obj['center']}. Iniciando centralizacao (center)")

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

        _log("[FASE 3] Objeto centralizado. Iniciando aproximacao (approach)")
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
        for i in range(4):
            angle = i * 90
            self._steps_taken.append(f"scan_frame_{i}")
            _log(f"  [scan {i}/4] Tirando foto na orientacao {angle} graus")

            try:
                camera_data = await asyncio.wait_for(
                    self._backend.get_camera(), timeout=CAMERA_TIMEOUT
                )
            except asyncio.TimeoutError:
                self._steps_taken.append("camera_timeout")
                _log(f"  [scan {i}/4] TIMEOUT da camera, pulando")
                continue
            except Exception:
                self._steps_taken.append("camera_error")
                _log(f"  [scan {i}/4] ERRO da camera, pulando")
                continue

            image_base64 = camera_data["image"]
            frame = decode_frame(image_base64)

            if frame is None or frame.shape[0] == 0:
                _log(f"  [scan {i}/4] Frame vazio, pulando")
                continue

            llm_description = self._original_description
            if not llm_description:
                llm_description = f"{object_color} {object_type}" if object_color else object_type

            _log(f"  [scan {i}/4] Perguntando para LLM se '{llm_description}' esta visivel...")
            llm_sees = await ask_llm_if_object_visible(
                self._llm_client, self._llm_model,
                image_base64, llm_description,
            )

            if not llm_sees:
                self._steps_taken.append(f"llm_not_found_at_{angle}deg")
                _log(f"  [scan {i}/4] LLM: NAO VIU objeto em {angle} graus")
                if i < 3:
                    _log(f"  [scan {i}/4] Girando -90 graus (esquerda)")
                    await self._rotate(-90)
                continue

            self._steps_taken.append(f"llm_detected_at_{angle}deg")
            _log(f"  [scan {i}/4] LLM: AVISTOU objeto em {angle} graus! Confirmando com OpenCV...")
            result = detect_object(frame, object_type, object_color)

            if result is not None:
                self._steps_taken.append(f"cv_confirmed_at_{angle}deg")
                _log(f"  [scan {i}/4] OpenCV: CONFIRMOU deteccao em {angle} graus. bbox={result['bbox']}")
                return {"object": result, "angle": angle}

            self._steps_taken.append(f"cv_not_confirmed_at_{angle}deg")
            _log(f"  [scan {i}/4] OpenCV: NAO CONFIRMOU. Marcando llm_spotted=True e continuando")
            self._llm_spotted = True
            self._llm_spotted_angle = angle
            if i < 3:
                _log(f"  [scan {i}/4] Girando -90 graus (esquerda)")
                await self._rotate(-90)

        _log(f"  [scan] Fim da varredura 360. llm_spotted={self._llm_spotted}")
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

    async def _targeted_opencv_sweep(self) -> dict | None:
        _log(f"  [targeted_sweep] LLM avistou a ~{self._llm_spotted_angle}graus. Varredura direcionada +-45graus + {TARGETED_SWEEP_ADVANCE_CM}cm")
        self._steps_taken.append("targeted_sweep_start")

        _log(f"  [targeted_sweep] Girando -{TARGETED_SWEEP_ANGLE}graus (esquerda)")
        await self._rotate(-TARGETED_SWEEP_ANGLE)
        _log(f"  [targeted_sweep] Avancando {TARGETED_SWEEP_ADVANCE_CM}cm")
        await self._move_forward(TARGETED_SWEEP_ADVANCE_CM)

        frame = await self._capture_frame()
        if frame is not None:
            _log("  [targeted_sweep] Tentando OpenCV apos -45graus + 50cm...")
            result = detect_object(frame, self._object_type, self._object_color)
            if result is not None:
                self._steps_taken.append("targeted_sweep_found_left")
                _log(f"  [targeted_sweep] OpenCV: DETECTOU! bbox={result['bbox']}")
                return {"object": result, "angle": self._llm_spotted_angle}
            _log("  [targeted_sweep] OpenCV: NAO detectou")

        _log(f"  [targeted_sweep] Voltando {TARGETED_SWEEP_ADVANCE_CM}cm")
        await self._move_backward(TARGETED_SWEEP_ADVANCE_CM)

        _log(f"  [targeted_sweep] Girando +{TARGETED_SWEEP_ANGLE * 2}graus (direita, passando pelo centro)")
        await self._rotate(TARGETED_SWEEP_ANGLE * 2)
        _log(f"  [targeted_sweep] Avancando {TARGETED_SWEEP_ADVANCE_CM}cm")
        await self._move_forward(TARGETED_SWEEP_ADVANCE_CM)

        frame = await self._capture_frame()
        if frame is not None:
            _log("  [targeted_sweep] Tentando OpenCV apos +45graus + 50cm...")
            result = detect_object(frame, self._object_type, self._object_color)
            if result is not None:
                self._steps_taken.append("targeted_sweep_found_right")
                _log(f"  [targeted_sweep] OpenCV: DETECTOU! bbox={result['bbox']}")
                return {"object": result, "angle": self._llm_spotted_angle}
            _log("  [targeted_sweep] OpenCV: NAO detectou")

        _log(f"  [targeted_sweep] Voltando {TARGETED_SWEEP_ADVANCE_CM}cm")
        await self._move_backward(TARGETED_SWEEP_ADVANCE_CM)

        _log("  [targeted_sweep] Fim da varredura direcionada. Nada encontrado")
        return None

    async def _explore_offsets(
        self, object_type: str, object_color: str | None, offset: int = EXPLORE_OFFSET_CM
    ) -> dict | None:
        _log(f"  [explore] Iniciando exploracao em {MAX_EXPLORE_DIRECTIONS} direcoes, offset={offset}cm")
        for direction in range(MAX_EXPLORE_DIRECTIONS):
            self._steps_taken.append(f"explore_direction_{direction}")
            _log(f"  [explore {direction}/{MAX_EXPLORE_DIRECTIONS}] Girando 90 graus para nova direcao")
            await self._rotate(90)

            _log(f"  [explore {direction}/{MAX_EXPLORE_DIRECTIONS}] Avancando {offset}cm")
            await self._move_forward(offset)

            frame = await self._capture_frame()
            if frame is None:
                _log(f"  [explore {direction}/{MAX_EXPLORE_DIRECTIONS}] Frame vazio, voltando")
                await self._move_backward(offset)
                continue

            try:
                camera_data = await asyncio.wait_for(
                    self._backend.get_camera(), timeout=CAMERA_TIMEOUT
                )
            except (asyncio.TimeoutError, Exception):
                _log(f"  [explore {direction}/{MAX_EXPLORE_DIRECTIONS}] Camera falhou, voltando")
                await self._move_backward(offset)
                continue

            image_base64 = camera_data["image"]
            llm_description = self._original_description
            if not llm_description:
                llm_description = f"{object_color} {object_type}" if object_color else object_type

            _log(f"  [explore {direction}/{MAX_EXPLORE_DIRECTIONS}] Perguntando para LLM...")
            llm_sees = await ask_llm_if_object_visible(
                self._llm_client, self._llm_model,
                image_base64, llm_description,
            )

            if not llm_sees:
                self._steps_taken.append(f"explore_dir_{direction}_llm_not_found")
                _log(f"  [explore {direction}/{MAX_EXPLORE_DIRECTIONS}] LLM: NAO VIU. Voltando {offset}cm")
                await self._move_backward(offset)
                continue

            self._steps_taken.append(f"explore_dir_{direction}_llm_detected")
            _log(f"  [explore {direction}/{MAX_EXPLORE_DIRECTIONS}] LLM: AVISTOU! Confirmando com OpenCV...")
            result = detect_object(frame, object_type, object_color)

            if result is not None:
                self._steps_taken.append(f"explore_cv_confirmed_dir_{direction}")
                _log(f"  [explore {direction}/{MAX_EXPLORE_DIRECTIONS}] OpenCV: CONFIRMOU! bbox={result['bbox']}")
                return {"object": result, "angle": direction * 90}

            self._steps_taken.append(f"explore_cv_not_confirmed_dir_{direction}")
            _log(f"  [explore {direction}/{MAX_EXPLORE_DIRECTIONS}] OpenCV: NAO CONFIRMOU. Voltando {offset}cm")
            await self._move_backward(offset)

        _log("  [explore] Fim da exploracao em cruz. Nada encontrado")
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
                    if rescan_count >= MAX_RESCANS:
                        return {"status": "not_found", "reason": "lost tracking after rescan"}
                    if not self._llm_spotted:
                        return {"status": "not_found", "reason": "lost tracking after rescan"}
                    _log("  [approach] Rescan nao encontrou mas llm_spotted=True, continuando")
                    continue
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
                    if rescan_count >= MAX_RESCANS:
                        return {"status": "not_found", "reason": "lost tracking after rescan"}
                    if not self._llm_spotted:
                        return {"status": "not_found", "reason": "lost tracking after rescan"}
                    _log("  [approach] Rescan nao encontrou mas llm_spotted=True, continuando")
                    continue
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
