import pytest
from flask import Flask


@pytest.fixture
def app_for_forms():
    app = Flask("forms_tester")
    app.config.update(
        SECRET_KEY="test",  # noqa: S106
        WTF_CSRF_ENABLED=False,
    )
    return app
