from enum import Enum, auto


class Status(Enum):
    ACCEPTED = auto()
    CANCELLED = auto()
    PENDING = auto()
    REJECTED = auto()
