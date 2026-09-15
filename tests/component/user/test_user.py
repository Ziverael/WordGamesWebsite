import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

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
        )
        edge2 = network_edge_factory.build(
            user_one_id=uuid.UUID("00000000-00000000-00000000-00000000"),
            user_two_id=uuid.UUID("00000000-00000000-00000000-00000001"),
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
