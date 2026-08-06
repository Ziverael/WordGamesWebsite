import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from word_games.user.db import User


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
