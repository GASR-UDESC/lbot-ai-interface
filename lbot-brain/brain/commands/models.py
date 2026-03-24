from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class WELL_DEFINED_MOVEMENT:
    input: Any
    output: Any


@dataclass(slots=True)
class BAD_DEFINED_MOVEMENT:
    input: Any
    output: Any


@dataclass(slots=True)
class LOCATION_MOVEMENT:
    input: Any
    output: Any


@dataclass(slots=True)
class VIEW:
    input: Any
    output: Any


@dataclass(slots=True)
class SPEAK:
    input: Any
    output: Any
