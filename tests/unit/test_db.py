import contextlib
from unittest.mock import Mock, call

from flask import g
from pytest_mock import MockFixture
from sqlalchemy.orm import Session

from word_games import db
from word_games.config.db import DATABASE_SETTINGS


def test_get_engine_creates_engine(mocker: MockFixture):
    # setup
    db.get_engine.cache_clear()

    # given
    mock_engine = Mock()
    create_engine_mock = mocker.patch.object(
        db,
        "create_engine",
        return_value=mock_engine,
    )

    # when
    engine = db.get_engine()

    # then
    assert engine is mock_engine
    assert create_engine_mock.call_count == 1
    assert create_engine_mock.call_args == call(
        url=DATABASE_SETTINGS.connection_string,
        pool_size=DATABASE_SETTINGS.pool_size,
        max_overflow=DATABASE_SETTINGS.max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


def test_get_engine_is_cached(mocker: MockFixture):
    # setup
    db.get_engine.cache_clear()

    # given
    mock_engine = Mock()
    create_engine_mock = mocker.patch.object(
        db,
        "create_engine",
        mock_engine,
    )

    # when
    engine1 = db.get_engine()
    engine2 = db.get_engine()

    # then
    assert engine1 is engine2
    assert create_engine_mock.call_count == 1


def test_session_factory():
    engine = object()
    factory = db.create_session_factory(engine)

    session = factory()

    assert isinstance(session, Session)
    assert session.bind is engine


def test_cleanup_commit(app_context):
    # given
    session = Mock()

    # when
    with app_context:
        g.db_session = session

    # then
    assert session.commit.call_count == 1
    assert session.rollback.call_count == 0
    assert session.close.call_count == 1


def test_cleanup_rollback(app_context):
    # given
    session = Mock()
    error_msg = "boom"

    def run_and_fail_app():
        with app_context:
            g.db_session = session
            raise ValueError(error_msg)

    # when
    with contextlib.suppress(ValueError):
        run_and_fail_app()

    # then
    session.commit.assert_not_called()
    session.rollback.assert_called_once()
    session.close.assert_called_once()
