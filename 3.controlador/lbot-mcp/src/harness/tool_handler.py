"""Rendering is separate from the structured result supplied to the model."""


def result_for_model(result: dict) -> dict:
    return {k: v for k, v in result.items() if k != "image"}


def result_for_display(result: dict) -> str:
    status = result.get("status", "unknown")
    reason = result.get("reason")
    if status in {"blocked", "failed", "cancelled", "timed_out"}:
        return f"{status}: {reason or 'motivo não informado'}" + (
            "; alvo detectado" if result.get("detected") else ""
        )
    if result.get("approached"):
        return f"{status}: aproximação verificada ({result.get('front_obstacle_distance_cm', '?')} cm)"
    if "detected" in result:
        return (
            f"{status}: objeto {'localizado' if result['detected'] else 'não localizado na busca limitada'}"
            + (f" ({reason})" if reason else "")
        )
    if "distance_cm" in result:
        return f"{status}: trajeto {result['distance_cm']:.1f} cm; rotação {result.get('rotation_degrees', 0):.1f}°"
    if "readings" in result:
        return (
            status
            + ": "
            + "; ".join(
                f"{name} {value} cm ({result.get('validity', {}).get(name, 'unknown')})"
                for name, value in result["readings"].items()
            )
        )
    if "frame_id" in result:
        return f"{status}: quadro {result['frame_id'][:8]}, revisão {result.get('revision', '?')}"
    return status + (f": {reason}" if reason else "")
