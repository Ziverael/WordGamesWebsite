import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import aliased

from word_games.db import get_session
from word_games.game.controller import Game
from word_games.task.controller import Task, TaskNaturalIdentifier
from word_games.user.controller import User


def select_task_description_where_assignee_and_creator(
    assignee: uuid.UUID, creator: uuid.UUID
):
    with get_session() as session:
        AssigneeUser = aliased(User)
        results = session.execute(
            select(
                Task.hrid,
                Task.assignee_id.label("assignee_public_id"),
                User.public_id.label("creator_public_id"),
                User.username.label("creator_username"),
                AssigneeUser.username.label("assignee_username"),
                Task.game_id,
                Game.type,
                Game.subtype,
                Task.solved,
                Task.created_at,
                Task.recently_viewed_at,
            )
            .join(Game, Game.public_id == Task.game_id)
            .join(User, User.id == Game.creator)
            .join(AssigneeUser, AssigneeUser.public_id == Task.assignee_id)
            .where(
                User.public_id == creator,
                Task.assignee_id == assignee,
            )
            .order_by(Task.hrid)
        )
        return results.mappings().all()


def select_task_description_where_assignee(
    assignee: uuid.UUID,
) -> list[TaskNaturalIdentifier]:
    with get_session() as session:
        AssigneeUser = aliased(User)
        results = session.execute(
            select(
                Task.hrid,
                Task.assignee_id.label("assignee_public_id"),
                User.public_id.label("creator_public_id"),
                User.username.label("creator_username"),
                AssigneeUser.username.label("assignee_username"),
                Task.game_id,
                Game.type,
                Game.subtype,
                Task.solved,
                Task.created_at,
                Task.recently_viewed_at,
            )
            .join(Game, Game.public_id == Task.game_id)
            .join(User, User.id == Game.creator)
            .join(AssigneeUser, AssigneeUser.public_id == Task.assignee_id)
            .where(
                Task.assignee_id == assignee,
            )
            .order_by(Task.hrid)
        )
        return results.mappings().all()


def select_task_description_where_creator(
    creator: uuid.UUID,
) -> list[TaskNaturalIdentifier]:
    with get_session() as session:
        AssigneeUser = aliased(User)
        results = session.execute(
            select(
                Task.hrid,
                Task.assignee_id.label("assignee_public_id"),
                User.public_id.label("creator_public_id"),
                User.username.label("creator_username"),
                AssigneeUser.username.label("assignee_username"),
                Task.game_id,
                Game.type,
                Game.subtype,
                Task.solved,
                Task.created_at,
                Task.recently_viewed_at,
            )
            .join(Game, Game.public_id == Task.game_id)
            .join(User, User.id == Game.creator)
            .join(AssigneeUser, AssigneeUser.public_id == Task.assignee_id)
            .where(
                User.public_id == creator,
            )
            .order_by(Task.hrid)
        )
        return results.mappings().all()


def select_task_natural_identifier_where_creator(
    creator: uuid.UUID,
) -> list[TaskNaturalIdentifier]:
    with get_session() as session:
        results = session.execute(
            select(
                Task.hrid,
                Task.assignee_id.label("assignee_public_id"),
                User.public_id.label("creator_public_id"),
            )
            .join(Game, Game.public_id == Task.game_id)
            .join(User, User.id == Game.creator)
            .where(User.public_id == creator)
            .order_by(Task.hrid)
        )
        return [
            TaskNaturalIdentifier.model_validate(row)
            for row in results.mappings()
        ]


def select_task_natural_identifier_where_assignee_and_creator(
    assignee: uuid.UUID, creator: uuid.UUID
) -> list[TaskNaturalIdentifier]:
    with get_session() as session:
        results = session.execute(
            select(
                Task.hrid,
                Task.assignee_id.label("assignee_public_id"),
                User.public_id.label("creator_public_id"),
            )
            .join(Game, Game.public_id == Task.game_id)
            .join(User, User.id == Game.creator)
            .where(
                User.public_id == creator,
                Task.assignee_id == assignee,
            )
            .order_by(Task.hrid)
        )
        return [
            TaskNaturalIdentifier.model_validate(row)
            for row in results.mappings()
        ]


def count_tasks_where_assignee_and_creator(
    assignee: uuid.UUID, creator: uuid.UUID
) -> list[TaskNaturalIdentifier]:
    with get_session() as session:
        results = session.execute(
            select(func.count(Task.id))
            .join(Game, Game.public_id == Task.game_id)
            .join(User, User.id == Game.creator)
            .where(
                User.public_id == creator,
                Task.assignee_id == assignee,
            )
        )
        return results.scalar_one()


def count_solved_tasks_where_assignee_and_creator(
    assignee: uuid.UUID, creator: uuid.UUID
) -> list[TaskNaturalIdentifier]:
    with get_session() as session:
        results = session.execute(
            select(func.count(Task.id))
            .join(Game, Game.public_id == Task.game_id)
            .join(User, User.id == Game.creator)
            .where(
                User.public_id == creator,
                Task.assignee_id == assignee,
                Task.solved.is_(True),
            )
        )
        return results.scalar_one()
