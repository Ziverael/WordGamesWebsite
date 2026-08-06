import pytest
from flask import template_rendered
from flask.ctx import AppContext
from flask.testing import FlaskClient
from flask_login import FlaskLoginClient
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.pytest_plugin import register_fixture

from word_games import create_app
from word_games.config.app import APP_SETTINGS
from word_games.game.db import Game
from word_games.task.db import Task
from word_games.user.db import User


@pytest.fixture(autouse=True)
def can_use_database() -> bool:
    return False


@pytest.fixture
def use_db(can_use_database: bool):
    if can_use_database:
        assert APP_SETTINGS.database_connection_string.startswith(
            "postgresql+psycopg://test_"
        ), "Test database must starts with 'test_' prefix"
    else:
        msg = "By default database is not available in tests."
        raise AssertionError(msg)


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
