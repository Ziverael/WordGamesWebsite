"""There are dedicated validators for game contents, to improve
restrictions per game.
"""

import json
from typing import Any, Final

from wtforms.validators import ValidationError


CHAR_LIMITS: Final[int] = 10_000


def fill_gaps_sentences(content: Any):
    if not isinstance(content, dict):
        msg = "Invalid content."
        raise ValidationError(msg)


def _basic_check(content: Any):
    content = _load_json(content)

    if not isinstance(content, list):
        msg = "Invalid content."
        raise ValidationError(msg)

    if len(content) > CHAR_LIMITS:
        msg = "Too many content elements."
        raise ValidationError(msg)

    for item in content:
        if not isinstance(item, dict):
            msg = "Invalid content element."
            raise ValidationError(msg)

        if not isinstance(item.get("text"), str):
            msg = "Invalid text."
            raise ValidationError(msg)

        if not isinstance(item.get("covered"), bool):
            msg = "Invalid covered value."
            raise ValidationError(msg)

        if len(item["text"]) > CHAR_LIMITS:
            msg = "Text is too long."
            raise ValidationError(msg)


def _load_json(content: Any):
    try:
        content = json.loads(content)
    except (TypeError, json.JSONDecodeError) as e:
        msg = "Content parsing error."
        raise ValidationError(msg) from e
    else:
        return content
