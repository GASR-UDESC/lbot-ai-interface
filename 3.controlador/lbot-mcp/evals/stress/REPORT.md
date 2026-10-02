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
  "count": 4,
  "success_rate": 1.0,
  "tool_selection_rate": 1.0,
  "categories": {
    "approach": {
      "count": 1,
      "success_rate": 1.0
    },
    "search": {
      "count": 3,
      "success_rate": 1.0
    }
  },
  "latency_p50_s": 10.205448791501112,
  "latency_p95_s": 41.44237570799305,
  "total_inference_calls": 18,
  "inference_latency_p50_s": 4.372974395999336,
  "inference_latency_p95_s": 5.6300259589916095,
  "resource_note": "process_max_rss is the evaluator peak (bytes on macOS); model/server RAM, GPU utilization, energy and temperature are measured separately or unavailable.",
  "invalid_calls": 0,
  "evaluation_note": "Success thresholds are goals, not automatically considered achieved."
}
```
