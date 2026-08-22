"""There are dedicated validators for game contents, to improve
restrictions per game.
"""

import json
import re
from typing import Any, Final

from wtforms.validators import ValidationError

from word_games.error import SecurityViolationError


CHAR_LIMITS: Final[int] = 10_000


def fill_gaps_sentences(content: Any):
    if content == "":
        msg = "Empty content"
        raise ValidationError(msg)
    _security_checks(content)
    json_content = load_json(content)
    if not isinstance(json_content, dict):
        msg = "Invalid content."
        raise ValidationError(msg)
    for sentence, marks in json_content.items():
        if not isinstance(sentence, str):
            msg = "Sentence should be a string."
            raise ValidationError(msg)
        if not isinstance(marks, list):
            msg = "Invalid item."
            raise ValidationError(msg)
        if len(marks) == 0:
            msg = ""
        if not (isinstance(el, str) for el in marks):
            msg = "Invalid marked object."


html_pattern = re.compile(r"<\s*/?\s*[a-zA-Z][^>]*>")


def _security_checks(content: str) -> None:
    """Checks for:
    1. Valid type
    2. Payload size
    3. code injection
    """
    if not isinstance(content, str):
        msg = "Content must be a string"
        raise SecurityViolationError(msg)
    if len(content) > CHAR_LIMITS:
        msg = f"Content exceeds the maximum allowed length of {CHAR_LIMITS} characters."
        raise SecurityViolationError(msg)
    if html_pattern.search(content):
        msg = "HTML markup is not allowed. This incident will be reported."
        raise SecurityViolationError(msg)


def load_json(content: Any):
    try:
        content = json.loads(content)
    except (TypeError, json.JSONDecodeError) as e:
        msg = "Content is not parseable."
        raise ValidationError(msg) from e
    else:
        return content
