import uuid

from word_games.error import WordGamesError
from word_games.model import Relation, Role
from word_games.user import db as _db
from word_games.user.db import User, select_user_exists_with_public_id


def get_public_id_by_id(id_: int) -> uuid.UUID:
    if (public_id := _db.select_public_id_where_id(id_)) is not None:
        return public_id
    msg = "No user with such id."
    raise WordGamesError(msg)


def get_user_id_by_username(username: str) -> uuid.UUID:
    if (user_id := _db.select_public_id_by_username(username)) is not None:
        return user_id
    msg = "Such user not exists."
    raise WordGamesError(msg)


def create_cn_relation_in_db(teacher: uuid.UUID, student: uuid.UUID) -> None:
    raise_if_user_not_exists(teacher)
    raise_if_user_not_exists(student)
    edge = _db.NetworkEdge(
        user_one_id=teacher,
        user_one_role=Role.teacher,
        user_two_id=student,
        user_two_role=Role.student,
    )
    _db.insert_community_network_edge(edge)


def delete_cn_relation_in_db(teacher: uuid.UUID, student: uuid.UUID) -> None:
    kwargs_opts: list[dict[str, uuid.UUID]] = [
        {
            "user_one_id": teacher,
            "user_two_id": student,
            "relation": Relation.teacher_student,
        },
        {
            "user_one_id": student,
            "user_two_id": teacher,
            "relation": Relation.student_teacher,
        },
    ]
    for kwargs in kwargs_opts:
        if _db.exists_community_network_edge(**kwargs):
            _db.delete_community_network_edge(**kwargs)
            return
    raise_cn_not_exists(student=student, teacher=teacher)


def get_user_teachers_and_students_public_ids(
    public_id: uuid.UUID,
) -> list[uuid.UUID]:
    raise_if_user_not_exists(public_id)
    id_role_pairs = _db.select_user_neighbors_with_their_roles(public_id)
    students = [id_ for id_, role in id_role_pairs if role == Role.student]
    teachers = [id_ for id_, role in id_role_pairs if role == Role.teacher]
    return teachers, students


def get_username_by_public_id(public_id: uuid.UUID) -> str:
    if (username := _db.select_username_where_public_id(public_id)) is not None:
        return username
    msg = "Such user not exists."
    raise WordGamesError(msg)


def get_role(public_id: uuid.UUID) -> Role:
    try:
        raise_if_user_not_exists(public_id)
        role = _db.select_user_role(public_id)
    except Exception as e:
        msg = "User not exists"
        raise WordGamesError(msg) from e
    else:
        return role


def raise_if_cn_relation_not_exists(
    user_one_id: uuid.UUID, user_two_id: uuid.UUID, relation: Relation
) -> None:
    if not _db.exists_community_network_edge(
        user_one_id, user_two_id, relation
    ):
        msg = f"Relation {relation} between {user_one_id} and {user_two_id} do not exists."
        raise WordGamesError(msg)


def raise_if_user_not_exists(public_id: uuid.UUID) -> None:
    if not select_user_exists_with_public_id(public_id):
        msg = f"User with public id {public_id}"
        raise WordGamesError(msg)


def raise_cn_not_exists(student: uuid.UUID, teacher: uuid.UUID) -> None:
    msg = f"Relation teacher({teacher}) student({student}) not exists"
    raise WordGamesError(msg)


__all__ = ["User"]
