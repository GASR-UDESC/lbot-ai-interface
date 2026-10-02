"""Local structured logs; camera pixels and credentials are deliberately omitted."""

import json
import os
import time
from pathlib import Path


def record(component, event, data):
    directory = Path(
        os.getenv("LBOT_TRACE_DIR", str(Path(__file__).resolve().parents[3] / "runs"))
    )
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / (component + ".jsonl")).open("a") as stream:
        stream.write(
            json.dumps(
                {"at": time.time(), "event": event, **data},
                ensure_ascii=False,
                default=str,
            )
            + "\n"
        )
