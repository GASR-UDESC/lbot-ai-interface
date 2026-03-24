from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Iterator

from openai import OpenAI


DEFAULT_SYSTEM_PROMPT = (
    "Voce e um assistente virtual inteligente e prestativo. "
    "Responda sempre em portugues de forma clara e concisa."
)


class LLM:
    """Encapsulates OpenAI-compatible chat client (LM Studio, Ollama, etc.)."""

    def __init__(
        self,
        api_base: str = "http://localhost:1234/v1",
        model: str = "local-model",
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> None:
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._history: list[dict[str, str]] = []

        self._client = OpenAI(base_url=api_base, api_key="lm-studio")
        self._client.models.list()

    def chat(self, user_message: str) -> str:
        """Sends a user message and returns full assistant response."""
        self._history.append({"role": "user", "content": user_message})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=self._build_messages(),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=False,
        )

        assistant_text = response.choices[0].message.content or ""
        self._history.append({"role": "assistant", "content": assistant_text})
        self._trim_history()
        return assistant_text

    def chat_stream(self, user_message: str) -> Iterator[str]:
        """Sends a user message and yields streamed tokens."""
        self._history.append({"role": "user", "content": user_message})

        stream = self._client.chat.completions.create(
            model=self.model,
            messages=self._build_messages(),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )

        full_response: list[str] = []
        for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            if token:
                full_response.append(token)
                yield token

        assistant_text = "".join(full_response)
        self._history.append({"role": "assistant", "content": assistant_text})
        self._trim_history()

    def chat_with_image(self, user_message: str, image_path: str | Path) -> str:
        """Sends a multimodal message (text + image) and returns full response."""
        image_file = Path(image_path).expanduser().resolve()
        if not image_file.exists():
            raise FileNotFoundError(f"Image file not found: {image_file}")

        mime_type, _ = mimetypes.guess_type(str(image_file))
        if mime_type is None:
            mime_type = "image/jpeg"

        image_b64 = base64.b64encode(image_file.read_bytes()).decode("ascii")
        image_data_url = f"data:{mime_type};base64,{image_b64}"

        self._history.append({"role": "user", "content": user_message})

        messages = self._build_messages()
        messages[-1] = {
            "role": "user",
            "content": [
                {"type": "text", "text": user_message},
                {"type": "image_url", "image_url": {"url": image_data_url}},
            ],
        }

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=False,
        )

        assistant_text = response.choices[0].message.content or ""
        self._history.append({"role": "assistant", "content": assistant_text})
        self._trim_history()
        return assistant_text

    def complete(self, messages: list[dict], temperature: float | None = None, max_tokens: int | None = None) -> str:
        """Runs a one-shot completion with explicit messages."""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature if temperature is None else temperature,
            max_tokens=self.max_tokens if max_tokens is None else max_tokens,
            stream=False,
        )
        return response.choices[0].message.content or ""

    def complete_with_image(
        self,
        prompt: str,
        image_path: str | Path,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Runs a one-shot multimodal completion (text + image)."""
        image_file = Path(image_path).expanduser().resolve()
        if not image_file.exists():
            raise FileNotFoundError(f"Image file not found: {image_file}")

        mime_type, _ = mimetypes.guess_type(str(image_file))
        if mime_type is None:
            mime_type = "image/jpeg"

        image_b64 = base64.b64encode(image_file.read_bytes()).decode("ascii")
        image_data_url = f"data:{mime_type};base64,{image_b64}"

        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            }
        )

        return self.complete(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def reset(self) -> None:
        """Clears conversation history."""
        self._history.clear()

    def _build_messages(self) -> list[dict[str, str]]:
        return [{"role": "system", "content": self.system_prompt}, *self._history]

    def _trim_history(self, max_turns: int = 20) -> None:
        max_messages = max_turns * 2
        if len(self._history) > max_messages:
            self._history = self._history[-max_messages:]
