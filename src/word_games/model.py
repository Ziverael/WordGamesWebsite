from enum import Enum, auto
from typing import Any


type Payload = dict[str, Any]


class Role(Enum):
    teacher = auto()
    student = auto()
