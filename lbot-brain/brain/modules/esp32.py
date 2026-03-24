from __future__ import annotations

from typing import Any


class ESP32:
    """Placeholder module for ESP32 integration.

    Current behavior is intentionally no-op.
    """

    def __init__(self) -> None:
        self._connected = False
        self._last_payload: Any = None

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self) -> None:
        """No-op placeholder for future connection logic."""

    def disconnect(self) -> None:
        """No-op placeholder for future disconnection logic."""

    def send(self, payload: Any) -> None:
        """No-op placeholder for future command transport."""
        self._last_payload = payload

    @property
    def last_payload(self) -> Any:
        return self._last_payload
