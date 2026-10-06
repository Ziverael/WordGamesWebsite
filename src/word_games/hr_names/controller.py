import secrets
import string
from typing import Final

from word_games.hr_names.adjectives import ADJECTIVES
from word_games.hr_names.nouns import NOUNS


RANDOM_SUFFIX_LENGTH: Final[int] = 6


def generate_hrid() -> str:
    id_ = f"{secrets.choice(ADJECTIVES)} {secrets.choice(NOUNS)}".lower()
    return id_.strip()


def generate_hruid(suffix_size: int = RANDOM_SUFFIX_LENGTH) -> str:
    hrid = generate_hrid()
    rand_suffix = "".join(
        secrets.choice(string.digits + string.ascii_letters)
        for _ in range(suffix_size)
    )
    return f"{hrid}_{rand_suffix}"
