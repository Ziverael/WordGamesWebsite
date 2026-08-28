import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, UUID, Index, delete, select
from sqlalchemy.orm import Mapped, mapped_column

from word_games.database import BaseTable
from word_games.db import get_session


class Game(BaseTable):
    """Is a set of challenges defined for a given game template. The game can
    be created by teacher. Object of game is created via game factory.

    Args:
        BaseTable (_type_): _description_
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    title: Mapped[str]
    type: Mapped[str]
    subtype: Mapped[str]
    created_at: Mapped[datetime]
    creator: Mapped[int]
    content: Mapped[dict] = mapped_column(JSON)

    __table_args__ = (
        Index("idx_unique_user_title", "creator", "title", unique=True),
    )


def select_public_business_columns(
    user_id: int,
) -> dict[str, Any]:
    with get_session() as session:
        results = session.execute(
            select(
                Game.title,
                Game.created_at,
                Game.public_id,
            ).where(Game.creator == user_id)
        )
        return results.mappings().all()


def select_user_game_titles_and_dates(
    user_id: int,
) -> list[tuple[str, datetime]]:
    with get_session() as session:
        results = session.execute(
            select(Game.title, Game.created_at).where(Game.creator == user_id)
        )
        return results.all()


def select_user_games_public_ids(user_id: int) -> list[int]:
    with get_session() as session:
        results = session.execute(
            select(Game.public_id).where(Game.creator == user_id)
        )
        return results.scalars()


def select_user_games_titles(user_id: int) -> list[int]:
    with get_session() as session:
        results = session.execute(
            select(Game.title).where(Game.creator == user_id)
        )
        return results.scalars()


def select_title_where_public_id(game_id: uuid.UUID) -> str:
    with get_session() as session:
        results = session.execute(
            select(Game.title).where(Game.public_id == game_id)
        )
        return results.scalar_one()


def delete_game_where_public_id(game_id: uuid.UUID) -> None:
    with get_session() as session:
        session.execute(delete(Game).where(Game.public_id == game_id))
