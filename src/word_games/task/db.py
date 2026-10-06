import uuid
from datetime import datetime

from sqlalchemy import (
    ForeignKeyConstraint,
    Index,
    delete,
    exists,
    func,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from word_games.database import BaseTable
from word_games.db import get_session


class Task(BaseTable):
    """Task is a declaration of assignment the Game for a user. Teacher can
    assigns a game to a student. There can be multiple tasks pointing the same
    game.

    Task names are human-redable identifiers (hrid) without random suffix. There are used
    to display them to users.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    hrid: Mapped[str]
    game_id: Mapped[uuid.UUID]
    assignee_id: Mapped[uuid.UUID]
    created_at: Mapped[datetime]
    viewed_at: Mapped[datetime | None]
    recently_viewed_at: Mapped[datetime | None]
    solved: Mapped[bool] = mapped_column(default=False)

    @property
    def task_name(self) -> str:
        return self.hrid.split("-")[0]

    __table_args__ = (
        Index("idx_unique_hrid", "hrid", unique=True),
        ForeignKeyConstraint(
            ["game_id"],
            ["game.public_id"],
            "fk_task_gameid_game",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["assignee_id"],
            ["user.public_id"],
            "fk_task_assigneeid_user",
            ondelete="CASCADE",
        ),
    )


class Results(BaseTable):
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[uuid.UUID]
    response: Mapped[dict] = mapped_column(JSONB)
    score: Mapped[int]
    max_score: Mapped[int]
    send_at: Mapped[datetime]


def select_hrid_exists(hrid: str) -> bool:
    with get_session() as session:
        results = session.execute(select(exists(Task).where(Task.hrid == hrid)))
        return results.scalar()


def select_game_id_where_hrid(hrid: str) -> uuid.UUID | None:
    with get_session() as session:
        results = session.execute(select(Task.game_id).where(Task.hrid == hrid))
        return results.scalar_one_or_none()


def update_viewed_at(ts: datetime, hrid: str) -> None:
    with get_session() as session:
        session.execute(
            update(Task).where(Task.hrid == hrid).values(viewed_at=ts)
        )


def update_recently_viewed_at(ts: datetime, hrid: str) -> None:
    with get_session() as session:
        session.execute(
            update(Task).where(Task.hrid == hrid).values(recently_viewed_at=ts)
        )


def delete_task_where_hrid(hrid: str) -> None:
    with get_session() as session:
        session.execute(delete(Task).where(Task.hrid == hrid))


def exists_task_where_assignee_id_and_game_id(
    assignee_id: uuid.UUID, game_id: uuid.UUID
) -> bool:
    with get_session() as session:
        results = session.execute(
            select(
                exists().where(
                    (Task.assignee_id == assignee_id)
                    & (Task.game_id == game_id)
                )
            )
        )
        return results.scalar_one()


def count_tasks_where_assignee_id(assignee_id: uuid.UUID) -> int:
    with get_session() as session:
        results = session.execute(
            select(func.count(Task.id)).where(Task.assignee_id == assignee_id)
        )
        return results.scalar_one()


def count_solved_tasks_where_assignee_id(assignee_id: uuid.UUID) -> int:
    with get_session() as session:
        results = session.execute(
            select(func.count(Task.id)).where(
                Task.assignee_id == assignee_id, Task.solved.is_(True)
            )
        )
        return results.scalar_one()
