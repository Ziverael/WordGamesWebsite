from datetime import datetime

from sqlalchemy import exists, select
from sqlalchemy.orm import Mapped, mapped_column

from word_games.database import BaseTable
from word_games.db import get_session


class Token(BaseTable):
    """Tracks tokens to avoid reusing and some offensive techniques on stoled tokens."""

    jti: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    purpose: Mapped[str]
    created_at: Mapped[datetime]
    expires_at: Mapped[datetime]
    used_at: Mapped[datetime]


def does_token_exists(jti: str) -> bool:
    with get_session() as session:
        return session.scalar(select(exists().where(Token.jti == jti)))


def insert_token(token: Token) -> None:
    with get_session() as session:
        return session.add(token)
