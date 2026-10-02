# Avaliação local (execução histórica)

Recalculada com validação independente dos sensores e do retorno da busca. Mantida para comparação; consulte `../acceptance-final/REPORT.md` para a versão final.

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
  "success_rate": 0.9333333333333333,
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
      "success_rate": 0.6
    },
    "sensors": {
      "count": 5,
      "success_rate": 1.0
    }
  },
  "latency_p50_s": 4.908377000014298,
  "latency_p95_s": 146.03802041697782,
  "total_inference_calls": 123,
  "inference_latency_p50_s": 4.088650999998208,
  "inference_latency_p95_s": 5.327050749998307,
  "resource_note": "process_max_rss is the evaluator peak (bytes on macOS); model/server RAM, GPU utilization, energy and temperature are measured separately or unavailable.",
  "invalid_calls": 0,
  "evaluation_note": "Scored with independent sensor readings and verified search return; historical execution retained, before final regression fixes."
}
```
