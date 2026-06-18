import pytest
from flask import template_rendered
from flask.ctx import AppContext
from flask.testing import FlaskClient
from flask_login import FlaskLoginClient
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.pytest_plugin import register_fixture

from word_games import create_app
from word_games.config.app import APP_SETTINGS
from word_games.db import SessionFactory, get_engine
from word_games.db_table import Game, Task, User


@pytest.fixture(autouse=True)
def use_db():
    assert APP_SETTINGS.SQLALCHEMY_DATABASE_URI.startswith(
        "postgresql+psycopg://test_"
    ), "Test database must starts with 'test_' prefix"


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    app.test_client_class = FlaskLoginClient
    return app


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def app_context(app) -> AppContext:
    return app.app_context()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def db_session():
    # setup
    connection = get_engine().connect()
    transaction = connection.begin()
    session = SessionFactory()

    yield session

    # teardown
    session.rollback()
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    yield recorded
    template_rendered.disconnect(record, app)


@register_fixture(name="game_factory")
class GameFactory(SQLAlchemyFactory[Game]): ...


@register_fixture(name="task_factory")
class TaskFactory(SQLAlchemyFactory[Task]): ...


@register_fixture(name="user_factory")
class UserFactory(SQLAlchemyFactory[User]): ...
