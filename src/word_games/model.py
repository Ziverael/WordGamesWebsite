from enum import Enum, StrEnum, auto
from typing import Any


type Payload = dict[str, Any]


class Role(StrEnum):
    teacher = auto()
    student = auto()


class Relation(Enum):
    teacher_student = auto()
    student_teacher = auto()
