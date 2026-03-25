"""
llm_client.py — LLM chat client via OpenAI-compatible API.

Connects to an OpenAI-compatible server (LM Studio, ollama, …) and provides
a chat interface with conversation history and streaming support.

Usage (standalone):
    python llm_client.py
    python llm_client.py --api-base http://localhost:11434/v1
"""

from __future__ import annotations

import sys
from typing import Iterator

from openai import OpenAI


_DEFAULT_SYSTEM_PROMPT = (
    "Você é um assistente virtual inteligente e prestativo. "
    "Responda sempre em português de forma clara e concisa."
)

_DEFAULT_API_BASE = "http://localhost:1234/v1"


class LLMClient:
    """Chat interface that delegates to an OpenAI-compatible API.

    Works out-of-the-box with LM Studio (default port 1234), ollama, or any
    server that exposes an ``/v1/chat/completions`` endpoint.

    Parameters
    ----------
    api_base : str
        Base URL of the API server.
    model : str
        Model identifier sent in the request (LM Studio ignores this when a
        single model is loaded, but it's required by the API schema).
    system_prompt : str
        System-level instruction prepended to every conversation.
    temperature : float
        Sampling temperature.
    max_tokens : int
        Maximum tokens per response.
    """

    def __init__(
        self,
        api_base: str = _DEFAULT_API_BASE,
        model: str = "local-model",
        system_prompt: str = _DEFAULT_SYSTEM_PROMPT,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> None:
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._history: list[dict[str, str]] = []

        self._client = OpenAI(base_url=api_base, api_key="lm-studio")

        # Validate connection on startup
        try:
            self._client.models.list()
        except Exception:
            sys.exit(
                f"\n[ERRO] Não foi possível conectar ao servidor LLM em {api_base}\n"
                f"       Verifique se o LM Studio está aberto e o servidor local está ativo.\n"
                f"       No LM Studio: Developer → Start Server  (porta 1234)\n"
            )

        print(f"✔ LLM conectado em {api_base}\n")

    # -- public API ---------------------------------------------------------

    def chat(self, user_message: str) -> str:
        """Send a message and return the full response."""
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
        """Send a message and yield response tokens as they are generated."""
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
            delta = chunk.choices[0].delta
            token = delta.content or ""
            if token:
                full_response.append(token)
                yield token

        assistant_text = "".join(full_response)
        self._history.append({"role": "assistant", "content": assistant_text})
        self._trim_history()

    def reset(self) -> None:
        """Clear conversation history."""
        self._history.clear()

    # -- internals ----------------------------------------------------------

    def _build_messages(self) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.system_prompt},
            *self._history,
        ]

    def _trim_history(self, max_turns: int = 20) -> None:
        """Keep only the last *max_turns* exchanges to avoid exceeding context."""
        max_messages = max_turns * 2
        if len(self._history) > max_messages:
            self._history = self._history[-max_messages:]


# -- standalone interactive mode --------------------------------------------

def _interactive(api_base: str, system_prompt: str) -> None:
    client = LLMClient(api_base=api_base, system_prompt=system_prompt)

    print("💬 Chat interativo (digite 'sair' para encerrar)\n")
    while True:
        try:
            user_input = input("\033[1mVocê:\033[0m ")
        except (EOFError, KeyboardInterrupt):
            print("\n\n⏹  Encerrado.")
            break

        if user_input.strip().lower() in ("sair", "exit", "quit"):
            print("⏹  Encerrado.")
            break

        if not user_input.strip():
            continue

        print("\033[96mLLM:\033[0m ", end="", flush=True)
        for token in client.chat_stream(user_input):
            print(token, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Chat interativo com LLM via API.")
    parser.add_argument(
        "--api-base",
        default=_DEFAULT_API_BASE,
        help=f"URL base da API OpenAI-compatible. Padrão: {_DEFAULT_API_BASE}",
    )
    parser.add_argument(
        "--system-prompt",
        default=_DEFAULT_SYSTEM_PROMPT,
        help="Prompt de sistema para o LLM.",
    )
    args = parser.parse_args()
    _interactive(args.api_base, args.system_prompt)
