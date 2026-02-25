from enum import Enum

class PlatformEnum(str, Enum):
    PYBIT = "pybit"
    MOEX = "moex"

class SecurityStatusEnum(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"

class SecurityTypeEnum(str, Enum):
    FUTURE = "future"
    EQUITY = "equity"
    OPTION = "option"

class FutureTypeEnum(str, Enum):
    LONG_TERM = "long_term"
    SHORT_TERM = "short_term"


class TimeframeEnum(str, Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    D1 = "D1"