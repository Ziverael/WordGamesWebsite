import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from word_games.user import db as _db
from word_games.user.db import (
    NetworkEdge,
    User,
    select_neighbours_of_user_where_public_id,
)


class TestUser:
    def test_insert(self, db_session, user_factory):
        # given
        user = user_factory.build()

        # when
        db_session.add(user)
        db_session.commit()

        # then
        stmt = select(User)
        users_in_db = db_session.scalars(stmt).all()
        assert len(users_in_db) == 1
        assert users_in_db[0] == user

    def test_unique_email_raises(self, db_session, user_factory):
        # given
        user1 = user_factory.build(email="test@example.com")
        user2 = user_factory.build(email="test@example.com")

        # when
        db_session.add(user1)
        db_session.commit()
        db_session.add(user2)

        # then
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestNetworkEdge:
    def test_insert(self, db_session, network_edge_factory):
        # given
        edge = network_edge_factory.build(
            user_one_id=uuid.UUID("00000000-00000000-00000000-00000000"),
            user_two_id=uuid.UUID("00000000-00000000-00000000-00000001"),
        )

        # when
        db_session.add(edge)
        db_session.commit()

        # then
        stmt = select(NetworkEdge)
        users_in_db = db_session.scalars(stmt).all()
        assert len(users_in_db) == 1
        assert users_in_db[0] == edge

    @pytest.mark.parametrize(
        ("uuid1", "uuid2"),
        [
            (
                "00000000-00000000-00000000-00000001",
                "00000000-00000000-00000000-00000000",
            ),
            (
                "00000000-00000000-00000000-00000000",
                "00000000-00000000-00000000-00000000",
            ),
        ],
    )
    def test_insert__violate_check(
        self, db_session, network_edge_factory, uuid1, uuid2
    ):
        # given
        edge = network_edge_factory.build(
            user_one_id=uuid.UUID(uuid1),
            user_two_id=uuid.UUID(uuid2),
        )

        # when
        db_session.add(edge)

        # then
        with pytest.raises(
            IntegrityError,
            match=r"new row for relation \"network_edge\" violates check constraint \"ck_ordered_id\"",
        ):
            db_session.commit()

    def test_unique_uuid_pair(self, db_session, network_edge_factory):
        # given
        edge1 = network_edge_factory.build(
            user_one_id=uuid.UUID("00000000-00000000-00000000-00000000"),
            user_two_id=uuid.UUID("00000000-00000000-00000000-00000001"),
            relation=_db.Relation.student_teacher,
        )
        edge2 = network_edge_factory.build(
            user_one_id=uuid.UUID("00000000-00000000-00000000-00000000"),
            user_two_id=uuid.UUID("00000000-00000000-00000000-00000001"),
            relation=_db.Relation.student_teacher,
        )

        # when
        db_session.add(edge1)
        db_session.commit()
        db_session.add(edge2)

        # then
        with pytest.raises(
            IntegrityError,
            match=r"duplicate key value violates unique constraint \"pk_network_edge\"",
        ):
            db_session.commit()


def test_select_neighbours_of_user_where_public_id(
    db_session, network_edge_factory
):
    # given
    for uuid1, uuid2 in [
        (
            "00000000-00000000-00000000-00000000",
            "00000000-00000000-00000000-00000001",
        ),
        (
            "00000000-00000000-00000000-00000000",
            "00000000-00000000-00000000-00000002",
        ),
        (
            "00000000-00000000-00000000-00000000",
            "00000000-00000000-00000000-00000003",
        ),
        (
            "00000000-00000000-00000000-00000001",
            "00000000-00000000-00000000-00000003",
        ),
        (
            "00000000-00000000-00000000-00000001",
            "00000000-00000000-00000000-00000004",
        ),
    ]:
        edge = network_edge_factory.build(
            user_one_id=uuid.UUID(uuid1),
            user_two_id=uuid.UUID(uuid2),
        )
        db_session.add(edge)
    db_session.commit()

    # when
    results = select_neighbours_of_user_where_public_id(
        public_id=uuid.UUID("00000000-00000000-00000000-00000000")
    )

    # then
    assert len(results) == 3
    assert sorted(results) == [
        uuid.UUID("00000000-00000000-00000000-00000001"),
        uuid.UUID("00000000-00000000-00000000-00000002"),
        uuid.UUID("00000000-00000000-00000000-00000003"),
    ]


def test_insert_community_network_edge(db_session, network_edge_factory):
    # given
    uuid1 = uuid.UUID("00000000-00000000-00000000-00000001")
    uuid2 = uuid.UUID("00000000-00000000-00000000-00000002")
    e = network_edge_factory.build(user_one_id=uuid1, user_two_id=uuid2)

    # when
    _db.insert_community_network_edge(e)

    # then
    stmt = select(_db.NetworkEdge)
    edges_in_db = db_session.scalars(stmt).all()
    assert len(edges_in_db) == 1
    assert edges_in_db == [e]


def test_insert_community_network_edge__none_passed(
    db_session, network_edge_factory
):
    # given
    e = None

    # when / then
    with pytest.raises(UnmappedInstanceError, match=r"NoneType' is not mapped"):
        _db.insert_community_network_edge(e)


def test_delete_community_network_edge(db_session, network_edge_factory):
    # given
    uuid1 = uuid.UUID("00000000-00000000-00000000-00000001")
    uuid2 = uuid.UUID("00000000-00000000-00000000-00000002")
    uuid3 = uuid.UUID("00000000-00000000-00000000-00000003")
    e1 = network_edge_factory.build(user_one_id=uuid1, user_two_id=uuid3)
    relation = _db.Relation.student_teacher
    e2 = _db.NetworkEdge(
        user_one_id=uuid1, user_two_id=uuid2, relation=relation
    )
    db_session.add(e1)
    db_session.add(e2)
    db_session.commit()

    # when
    _db.delete_community_network_edge(
        user_one_id=uuid1, user_two_id=uuid2, relation=relation
    )

    # then
    stmt = select(_db.NetworkEdge)
    edges_in_db = db_session.scalars(stmt).all()
    assert len(edges_in_db) == 1
    assert edges_in_db == [e1]


def test_delete_community_network_edge__similar_relation(db_session):
    # given
    uuid1 = uuid.UUID("00000000-00000000-00000000-00000001")
    uuid2 = uuid.UUID("00000000-00000000-00000000-00000002")
    relation1 = _db.Relation.student_teacher
    relation2 = _db.Relation.teacher_student
    e1 = _db.NetworkEdge(
        user_one_id=uuid1, user_two_id=uuid2, relation=relation1
    )
    e2 = _db.NetworkEdge(
        user_one_id=uuid1, user_two_id=uuid2, relation=relation2
    )
    db_session.add(e1)
    db_session.add(e2)
    db_session.commit()

    # when
    _db.delete_community_network_edge(
        user_one_id=uuid1, user_two_id=uuid2, relation=relation1
    )

    # then
    stmt = select(_db.NetworkEdge)
    edges_in_db = db_session.scalars(stmt).all()
    assert len(edges_in_db) == 1
    assert edges_in_db == [e2]


def test_delete_community_network_edge__not_matching_relation(db_session):
    # given
    uuid1 = uuid.UUID("00000000-00000000-00000000-00000001")
    uuid2 = uuid.UUID("00000000-00000000-00000000-00000002")
    relation1 = _db.Relation.student_teacher
    relation2 = _db.Relation.teacher_student
    e1 = _db.NetworkEdge(
        user_one_id=uuid1, user_two_id=uuid2, relation=relation1
    )
    e2 = _db.NetworkEdge(
        user_one_id=uuid1, user_two_id=uuid2, relation=relation2
    )
    db_session.add(e1)
    db_session.add(e2)
    db_session.commit()

    # when
    _db.delete_community_network_edge(
        user_one_id=uuid1, user_two_id=uuid2, relation=relation1
    )

    # then
    stmt = select(_db.NetworkEdge)
    edges_in_db = db_session.scalars(stmt).all()
    assert len(edges_in_db) == 1
    assert edges_in_db == [e2]


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        (
            (
                uuid.UUID("00000000-00000000-00000000-00000001"),
                uuid.UUID("00000000-00000000-00000000-00000002"),
                _db.Relation.student_teacher,
            ),
            True,
        ),
        (
            (
                uuid.UUID("00000000-00000000-00000000-00000001"),
                uuid.UUID("00000000-00000000-00000000-00000002"),
                _db.Relation.teacher_student,
            ),
            False,
        ),
        (
            (
                uuid.UUID("00000000-00000000-00000000-00000002"),
                uuid.UUID("00000000-00000000-00000000-00000003"),
                _db.Relation.student_teacher,
            ),
            False,
        ),
    ],
)
def test_exists_community_network_edge(db_session, input: list, expected: bool):
    # given
    uuid1 = uuid.UUID("00000000-00000000-00000000-00000001")
    uuid2 = uuid.UUID("00000000-00000000-00000000-00000002")
    uuid3 = uuid.UUID("00000000-00000000-00000000-00000003")
    relation1 = _db.Relation.student_teacher
    relation2 = _db.Relation.teacher_student
    e1 = _db.NetworkEdge(
        user_one_id=uuid1, user_two_id=uuid2, relation=relation1
    )
    e2 = _db.NetworkEdge(
        user_one_id=uuid1, user_two_id=uuid3, relation=relation2
    )
    db_session.add(e1)
    db_session.add(e2)
    db_session.commit()

    # when
    results = _db.exists_community_network_edge(*input)

    # then
    assert results == expected


@pytest.mark.parametrize(
    ("edges_in_db", "expected"),
    [
        (
            (
                {
                    "user_one_id": uuid.UUID(
                        "00000000-00000000-00000000-00000001"
                    ),
                    "user_two_id": uuid.UUID(
                        "00000000-00000000-00000000-00000002"
                    ),
                    "relation": _db.Relation.student_teacher,
                },
            ),
            [],
        ),
        (
            (
                {
                    "user_one_id": uuid.UUID(
                        "00000000-00000000-00000000-00000000"
                    ),
                    "user_two_id": uuid.UUID(
                        "00000000-00000000-00000000-00000002"
                    ),
                    "relation": _db.Relation.student_teacher,
                },
            ),
            [
                (
                    uuid.UUID("00000000-00000000-00000000-00000002"),
                    _db.Role.teacher,
                )
            ],
        ),
        (
            (
                {
                    "user_one_id": uuid.UUID(
                        "00000000-00000000-00000000-00000000"
                    ),
                    "user_two_id": uuid.UUID(
                        "00000000-00000000-00000000-00000001"
                    ),
                    "relation": _db.Relation.teacher_student,
                },
            ),
            [
                (
                    uuid.UUID("00000000-00000000-00000000-00000001"),
                    _db.Role.student,
                )
            ],
        ),
    ],
)
def test_select_user_neighbors_with_their_roles(
    db_session, network_edge_factory, edges_in_db: dict, expected: bool
):
    # given
    for edge in edges_in_db:
        e = network_edge_factory.build(**edge)
        db_session.add(e)
    db_session.commit()
    public_id = uuid.UUID("00000000-00000000-00000000-00000000")

    # when
    results = _db.select_user_neighbors_with_their_roles(public_id)

    # then
    assert results == expected


@pytest.mark.parametrize(
    ("edges_in_db", "expected"),
    [
        (
            (
                {
                    "user_one_id": uuid.UUID(
                        "00000000-00000000-00000000-00000001"
                    ),
                    "user_two_id": uuid.UUID(
                        "00000000-00000000-00000000-00000002"
                    ),
                    "relation": _db.Relation.student_teacher,
                },
            ),
            [],
        ),
        (
            (
                {
                    "user_one_id": uuid.UUID(
                        "00000000-00000000-00000000-00000002"
                    ),
                    "user_two_id": uuid.UUID(
                        "00000000-00000000-00000000-00000010"
                    ),
                    "relation": _db.Relation.student_teacher,
                },
            ),
            [
                (
                    uuid.UUID("00000000-00000000-00000000-00000002"),
                    _db.Role.student,
                )
            ],
        ),
        (
            (
                {
                    "user_one_id": uuid.UUID(
                        "00000000-00000000-00000000-00000001"
                    ),
                    "user_two_id": uuid.UUID(
                        "00000000-00000000-00000000-00000010"
                    ),
                    "relation": _db.Relation.teacher_student,
                },
            ),
            [
                (
                    uuid.UUID("00000000-00000000-00000000-00000001"),
                    _db.Role.teacher,
                )
            ],
        ),
    ],
)
def test_select_user_neighbors_with_their_roles2(
    db_session, network_edge_factory, edges_in_db: dict, expected: bool
):
    # given
    for edge in edges_in_db:
        e = network_edge_factory.build(**edge)
        db_session.add(e)
    db_session.commit()
    public_id = uuid.UUID("00000000-00000000-00000000-00000010")

    # when
    results = _db.select_user_neighbors_with_their_roles(public_id)

    # then
    assert results == expected


@pytest.mark.parametrize(
    ("public_id", "expected"),
    [
        (uuid.UUID("00000000-00000000-00000000-00000000"), True),
        (uuid.UUID("00000000-00000000-00000000-00000010"), False),
    ],
)
def test_select_user_exists_with_public_id(
    db_session, user_factory, public_id, expected
):
    # given
    for id_ in [
        uuid.UUID("00000000-00000000-00000000-00000000"),
        uuid.UUID("00000000-00000000-00000000-00000001"),
    ]:
        user = user_factory.build(public_id=id_)
        db_session.add(user)
    db_session.commit()

    # when
    results = _db.select_user_exists_with_public_id(public_id)

    # then
    assert results == expected


@pytest.mark.parametrize(
    ("user_args_in_db", "expected"),
    [
        (
            {
                "public_id": uuid.UUID("00000000-00000000-00000000-00000000"),
                "role": _db.Role.student,
            },
            _db.Role.student,
        ),
        (
            {
                "public_id": uuid.UUID("00000000-00000000-00000000-00000000"),
                "role": _db.Role.teacher,
            },
            _db.Role.teacher,
        ),
        (
            {},
            None,
        ),
    ],
)
def test_select_user_role(db_session, user_factory, user_args_in_db, expected):
    # given
    uuid_ = uuid.UUID("00000000-00000000-00000000-00000000")
    user = user_factory.build(**user_args_in_db)
    db_session.add(user)
    db_session.commit()

    # when
    results = _db.select_user_role(uuid_)

    # then
    assert results == expected
