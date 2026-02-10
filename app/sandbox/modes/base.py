from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class ModeResult:
    next_mode: Optional[str] = None
    output: Optional[str] = None
    stop: bool = False



@dataclass
class DispatchResult:
    ok: bool
    value: Optional[Any] = None
    error: Optional[str] = None
