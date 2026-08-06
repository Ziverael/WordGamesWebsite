import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from word_games.task.db import Task


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
