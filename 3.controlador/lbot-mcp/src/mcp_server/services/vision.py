import base64
import json

import cv2
from jsonschema import Draft202012Validator

from .detector import decode_frame, parse_description, propose_regions
from .inference import get_inference

VISION_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["detected", "not_detected", "inconclusive"],
        },
        "candidate_id": {"type": ["integer", "null"]},
        "bbox": {
            "type": ["array", "null"],
            "items": {"type": "number", "minimum": 0, "maximum": 1000},
            "minItems": 4,
            "maxItems": 4,
        },
        "sensor_association": {"type": "boolean"},
    },
    "required": ["status", "candidate_id", "bbox", "sensor_association"],
    "additionalProperties": False,
}


async def locate_object(camera: dict, description: str) -> dict:
    frame = decode_frame(camera["image"])
    _, color = parse_description(description)
    candidates = propose_regions(frame, color)
    annotated = frame.copy()
    for i, (x, y, w, h) in enumerate(candidates):
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (255, 255, 255), 1)
        cv2.putText(
            annotated,
            str(i),
            (x, max(15, y - 3)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            2,
        )
    _, png = cv2.imencode(".png", annotated)
    crops = []
    for i, (x, y, w, h) in enumerate(candidates[:4]):
        crop = frame[
            max(0, y - 4) : min(frame.shape[0], y + h + 4),
            max(0, x - 4) : min(frame.shape[1], x + w + 4),
        ]
        crop = cv2.resize(crop, (224, 224))
        _, encoded = cv2.imencode(".png", crop)
        crops.extend(
            [
                {
                    "type": "text",
                    "text": f"Região candidata {i}, ampliada apenas para identificação:",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/png;base64,"
                        + base64.b64encode(encoded).decode()
                    },
                },
            ]
        )
    response = await get_inference().complete(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Localize {description} nesta câmera frontal. As caixas numeradas são regiões candidatas, não identidades conhecidas. Escolha candidate_id se uma caixa contém o alvo. Retorne detected somente se ele está visível. Se nenhuma caixa cobre um alvo visível, use bbox [left,top,right,bottom] em coordenadas normalizadas de 0 a 1000, NÃO em pixels; caso contrário bbox=null. status=not_detected se não está visível, inconclusive se não consegue decidir. sensor_association=true SOMENTE se o alvo está centralizado e não há obstáculo entre a câmera e ele. Céu, chão e números não são objetos. Regiões em pixels: "
                        + json.dumps(candidates),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/png;base64,"
                            + base64.b64encode(png).decode()
                        },
                    },
                ]
                + crops,
            }
        ],
        temperature=0.0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "object_location",
                "strict": True,
                "schema": VISION_SCHEMA,
            },
        },
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("vision_empty_response")
    data = json.loads(content)
    try:
        Draft202012Validator(VISION_SCHEMA).validate(data)
    except Exception as e:
        raise RuntimeError("vision_invalid_response") from e
    if data.get("status") not in {"detected", "not_detected", "inconclusive"}:
        raise RuntimeError("vision_invalid_response")
    if data["status"] == "detected":
        candidate = data.get("candidate_id")
        if isinstance(candidate, int) and 0 <= candidate < len(candidates):
            box = candidates[candidate]
        else:
            box = data.get("bbox")
            if not isinstance(box, list) or len(box) != 4:
                raise RuntimeError("vision_invalid_bbox")
            x1, y1, x2, y2 = box
            intr = camera["intrinsics"]
            w, h = intr["width"], intr["height"]
            if not 0 <= x1 < x2 <= 1000 or not 0 <= y1 < y2 <= 1000:
                raise RuntimeError("vision_invalid_bbox")
            box = [
                x1 * w / 1000,
                y1 * h / 1000,
                (x2 - x1) * w / 1000,
                (y2 - y1) * h / 1000,
            ]
        data["bbox"] = box
        intr = camera["intrinsics"]
        cx = box[0] + box[2] / 2
        data["sensor_association"] = bool(data.get("sensor_association")) and abs(
            cx - intr["cx"]
        ) <= min(16, max(4, box[2] / 4))
    return {
        **data,
        "frame_id": camera["frame_id"],
        "session_id": camera["session_id"],
        "revision": camera["revision"],
    }
