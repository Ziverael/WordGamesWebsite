import pytest
from flask import g
from sqlalchemy.orm import sessionmaker

from word_games.db import get_engine


@pytest.fixture(autouse=True)
def can_use_database() -> bool:
    return True


@pytest.fixture
def db_session():
    """This should be fixed. Actually there are 3 independent sessions their
    concurring in tests: this one, Flask Login Client session and session from
    flask.
    """
    connection = get_engine().connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def app_db_session(app, db_session):
    with app.app_context():
        g.db_session = db_session
        yield
        g.pop("db_session", None)


@pytest.fixture
def app_for_forms(app):
    app.config.update(
        {
            "SECRET_KEY": "test",
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        }
    )
    return app
