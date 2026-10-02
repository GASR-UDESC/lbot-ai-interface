# Avaliação local

Modelo: Qwen3.5 4B. Resultados verificados pelo estado diagnóstico, sem fornecer ground truth ao agente.

```json
{
  "model": "qwen3.5-4b",
  "runtime": {
    "python": "3.12.11",
    "platform": "macOS-27.0.1-arm64-arm-64bit",
    "machine": "arm64",
    "context_tokens": 8192,
    "temperature": 0.2,
    "reasoning_effort": "none",
    "seed": 42
  },
  "count": 30,
  "success_rate": 1.0,
  "tool_selection_rate": 1.0,
  "categories": {
    "approach": {
      "count": 5,
      "success_rate": 1.0
    },
    "conversation": {
      "count": 5,
      "success_rate": 1.0
    },
    "movement": {
      "count": 5,
      "success_rate": 1.0
    },
    "observation": {
      "count": 5,
      "success_rate": 1.0
    },
    "search": {
      "count": 5,
      "success_rate": 1.0
    },
    "sensors": {
      "count": 5,
      "success_rate": 1.0
    }
  },
  "latency_p50_s": 4.8815974584867945,
  "latency_p95_s": 148.44707441600622,
  "total_inference_calls": 124,
  "inference_latency_p50_s": 4.103141770494403,
  "inference_latency_p95_s": 5.369430416991236,
  "resource_note": "process_max_rss is the evaluator peak (bytes on macOS); model/server RAM, GPU utilization, energy and temperature are measured separately or unavailable.",
  "invalid_calls": 0,
  "evaluation_note": "Success thresholds are goals, not automatically considered achieved."
}
```
