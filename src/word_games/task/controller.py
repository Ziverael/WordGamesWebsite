import uuid
from datetime import datetime
from typing import Never

from word_games.db import get_session
from word_games.error import WordGamesError
from word_games.game.controller import raise_if_user_is_not_the_game_owner
from word_games.hr_names.controller import generate_hruid
from word_games.task import db as _db
from word_games.task.db import Task
from word_games.task.model import TaskNaturalIdentifier
from word_games.utils import TZ_UTC


def add_task_to_db(
    game_id: uuid.UUID, assignee_id: uuid.UUID, created_at: datetime | None
) -> None:
    raise_if_game_already_assigned_to_user(game_id, assignee_id)
    retries = 10
    for _ in range(retries):
        if not _db.select_hrid_exists(hrid := generate_hruid()):
            break
    else:
        msg = "Failed to create new task."
        raise WordGamesError(msg)
    task = Task(
        hrid=hrid,
        game_id=game_id,
        assignee_id=assignee_id,
        created_at=created_at or datetime.now(tz=TZ_UTC),
    )
    with get_session() as session:
        session.add(task)


def delete_task_from_db(hrid: str, user_public_id: uuid.UUID) -> None:
    try:
        raise_if_task_with_hrid_not_exists(hrid)
        game_id = _db.select_game_id_where_hrid(hrid)
        raise_if_user_is_not_the_game_owner(
            user_public_id=user_public_id, game_id=game_id
        )
        _db.delete_task_where_hrid(hrid)
    except Exception as e:
        msg = f"Cannot delete task with hrid {hrid}."
        raise WordGamesError(msg) from e


def count_student_tasks(public_id: uuid.UUID) -> int:
    try:
        results = _db.count_tasks_where_assignee_id(public_id)
    except Exception as e:
        msg = f"Cannot count tasks for assignee {public_id}."
        raise WordGamesError(msg) from e
    else:
        return results


def count_solved_student_tasks(public_id: uuid.UUID) -> int:
    try:
        results = _db.count_solved_tasks_where_assignee_id(public_id)
    except Exception as e:
        msg = f"Cannot count solved tasks for assignee {public_id}."
        raise WordGamesError(msg) from e
    else:
        return results


def raise_if_task_with_hrid_not_exists(hrid: str) -> None:
    if not _db.select_hrid_exists(hrid):
        msg = f"Task with hrid {hrid} not exists."
        raise WordGamesError(msg)


def raise_if_game_already_assigned_to_user(
    game_id: uuid.UUID, user_id: uuid.UUID
) -> Never:
    if _db.exists_task_where_assignee_id_and_game_id(
        assignee_id=user_id, game_id=game_id
    ):
        msg = "This game is already assigned to this student."
        raise WordGamesError(msg)


__all__ = ["TaskNaturalIdentifier"]
