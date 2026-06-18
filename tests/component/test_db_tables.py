import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from word_games.db_table import Game, Task, User


class TestGame:
    def test_insert(self, db_session, game_factory):
        # given
        game = game_factory.build()

        # when
        db_session.add(game)
        db_session.commit()

        # then
        stmt = select(Game)
        games_in_db = db_session.scalars(stmt).all()
        assert len(games_in_db) == 1
        assert games_in_db[0] == game

    def test_unique_id(self, db_session, game_factory):
        # given
        game1 = game_factory.build(id=1)
        game2 = game_factory.build(id=1)

        # when
        db_session.add(game1)
        db_session.commit()
        db_session.add(game2)

        # then
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestTask:
    def test_insert(self, db_session, task_factory):
        # given
        task = task_factory.build()

        # when
        db_session.add(task)
        db_session.commit()

        # then
        stmt = select(Task)
        tasks_in_db = db_session.scalars(stmt).all()
        assert len(tasks_in_db) == 1
        assert tasks_in_db[0] == task

    def test_unique_id(self, db_session, task_factory):
        # given
        task1 = task_factory.build(id=1)
        task2 = task_factory.build(id=1)

        # when
        db_session.add(task1)
        db_session.commit()
        db_session.add(task2)

        # then
        with pytest.raises(IntegrityError):
            db_session.commit()


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
