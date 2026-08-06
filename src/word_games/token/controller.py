import secrets
from datetime import datetime, timedelta
from typing import Any

import jwt
from flask import current_app

from word_games.constants import TOKEN_EXP_TIME_SEC
from word_games.error import TokenError, ValidationError
from word_games.model import Payload
from word_games.token._constants import (
    JTI_LENGTH,
    JWT_PAYLOAD_VERSION,
)
from word_games.token.db import does_token_exists
from word_games.utils import TZ_UTC


def _check_payload_before_serialization(payload: Payload) -> None:
    for flag in ["purpose", "user_id"]:
        if flag not in payload:
            msg = f"Missing field '{flag}' in token."
            raise TokenError(msg)


def _check_payload_after_deserialization(payload: Payload) -> None:
    if payload.get("version") != JWT_PAYLOAD_VERSION:
        msg = "Unsupported token version."
        raise TokenError(msg)
    for flag in ["purpose", "user_id", "jti", "nbf", "iat", "exp"]:
        if flag not in payload:
            msg = f"Missing field '{flag}' in token."
            raise TokenError(msg)
    if does_token_exists(payload["jti"]):
        log_token_usage_incident()
        msg = "Token already used."
        raise TokenError(msg)
    now = datetime.now(TZ_UTC)
    nbf = datetime.fromtimestamp(payload["nbf"], tz=TZ_UTC)
    if now < nbf:
        log_token_usage_incident()
        msg = "Token is not available."
        raise TokenError(msg)
    exp = datetime.fromtimestamp(payload["exp"], tz=TZ_UTC)
    if now > exp:
        log_token_usage_incident()
        msg = "Token expired."
        raise TokenError(msg)


def serialize(payload: Payload, expriration_time: int = TOKEN_EXP_TIME_SEC):
    try:
        _check_payload_before_serialization(payload)
        now = datetime.now(TZ_UTC)
        output = jwt.encode(
            {
                **payload,
                "nbf": now,
                "iat": now,
                "exp": now + timedelta(seconds=expriration_time),
                "jti": secrets.token_hex(JTI_LENGTH),
                "version": JWT_PAYLOAD_VERSION,
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )
    except (TypeError, ValueError, ValidationError) as e:
        msg = "Serialization failed"
        raise TokenError(msg) from e
    else:
        return output


def deserialize(token: str) -> dict[str, Any]:
    try:
        output = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            leeway=timedelta(seconds=10),
            algorithms=["HS256"],
        )
        _check_payload_after_deserialization(output)
    except jwt.ExpiredSignatureError as e:
        msg = "Token expired"
        raise TokenError(msg) from e
    except jwt.InvalidTokenError as e:
        msg = "Invalid token"
        raise TokenError(msg) from e
    else:
        return output


def log_token_usage_incident(): ...  # TODO #noqa:FIX002
