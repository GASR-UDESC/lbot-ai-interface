"""LBML grammar. Completion is reported by the backend, never estimated here."""

import re
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    type: str
    value: int
    direction: str


def parse_lbml_sequence(text: str) -> list[ParsedCommand] | None:
    if not isinstance(text, str) or not re.fullmatch(
        r"(?:D[1-9]\d*[FBLR];|R[1-9]\d*[LR];)+", text
    ):
        return None
    result = [
        ParsedCommand(kind, int(value), direction)
        for kind, value, direction in re.findall(r"([DR])(\d+)([FBLR]);", text)
    ]
    if len(result) > 64 or any(
        c.value > (400 if c.type == "D" else 720) for c in result
    ):
        return None
    return result


def validate_lbml(text: str) -> bool:
    return parse_lbml_sequence(text) is not None
