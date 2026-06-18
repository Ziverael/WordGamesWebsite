from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import jwt
from flask import current_app

from word_games.constants import ENCODING, TOKEN_EXP_TIME_SEC
from word_games.error import TokenError


TZ_UTC = ZoneInfo("UTC")


def serialize(
    payload: dict[str, Any], expriration_time: int = TOKEN_EXP_TIME_SEC
):
    try:
        output = jwt.encode(
            payload
            | {
                "exp": datetime.now(TZ_UTC)
                + timedelta(seconds=expriration_time)
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).encode(ENCODING)
    except jwt.exceptions.DecodeError as e:
        msg = "Serialization failed."
        raise TokenError(msg) from e
    else:
        return output


def deserialize(token: bytes):
    try:
        output = jwt.decode(
            token.decode(ENCODING),
            current_app.config["SECRET_KEY"],
            leeway=timedelta(seconds=10),
            algorithms=["HS256"],
        )
    except jwt.exceptions.DecodeError as e:
        msg = "Deserialization failed."
        raise TokenError(msg) from e
    else:
        return output


# TODO: implement url_has_allowed_host_and_scheme: https://github.com/django/django/blob/4.0/django/utils/http.py#L239  # noqa: FIX002
