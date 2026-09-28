import uuid

from word_games.error import WordGamesError
from word_games.model import Relation, Role
from word_games.user import db as _db
from word_games.user.db import select_user_exists_with_public_id


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


def get_user_teachers_and_students_public_ids(
    public_id: uuid.UUID,
) -> list[uuid.UUID]:
    raise_if_user_not_exists(public_id)
    id_role_pairs = _db.select_user_neighbors_with_their_roles(public_id)
    students = [id_ for id_, role in id_role_pairs if role == Role.student]
    teachers = [id_ for id_, role in id_role_pairs if role == Role.teachers]
    return teachers, students


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
