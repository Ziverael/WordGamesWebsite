"""
Crosswords:
1. Free form - The shape and size grow or shrink depending on how the words intersect
2. codeword - this one is a complete crossword grid where each letter of the alphabet is substituted for a number (usually 1-26). There is a minimum one occurrence of each letter of the alphabet.
There are few letters given as starters. The solver has to decipher the rest of the code to discover the words in the completed puzzle.
3. blocked grid - whole crossword is placed in a square plane. Words are placed on a grid.
Words can be separated by empty squares.
"""

from datetime import datetime
from enum import StrEnum, auto
from typing import Any, Final

from pydantic import BaseModel, Field


class GameNaturalIdentifier(BaseModel):
    creator: int
    title: str = Field(min_length=1)


class GameUpdate(BaseModel):
    modified_at: datetime
    content: Any


class GameType(StrEnum):
    crossword = auto()
    matching = auto()
    quiz = auto()
    fill_gaps = auto()


GAME_LAYOUTS: Final[dict[str, list[str]]] = {
    GameType.crossword.value: [
        "freeform",
        "codeword",
        "blocked grid",
    ],
    GameType.matching.value: [
        "left to right",
        "conveyor belt",
        "grid",
    ],
    GameType.quiz.value: [
        "wit timer",
        "timeless",
    ],
    GameType.fill_gaps.value: [
        "sentences",
        "words",
    ],
}
