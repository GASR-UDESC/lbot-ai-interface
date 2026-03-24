from __future__ import annotations

from pathlib import Path


class Camera:
    """Mock camera module that always returns a static image."""

    def __init__(self, mock_image_path: str | Path | None = None) -> None:
        default_mock = Path(__file__).resolve().parents[2] / "image.jpg"
        self._mock_image_path = Path(mock_image_path or default_mock).expanduser().resolve()

        if not self._mock_image_path.exists():
            raise FileNotFoundError(
                f"Mock camera image not found: {self._mock_image_path}"
            )

    def capture(self) -> Path:
        """Returns the mock image path as the captured frame."""
        return self._mock_image_path
