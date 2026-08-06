from typing import cast
from unittest.mock import Mock, call

import pytest
from flask import Flask
from pytest_mock import MockFixture

import word_games.email.resend_adapter
import word_games.email.smtp_adapter
import word_games.extensions
from word_games.config.app import APP_SETTINGS
from word_games.email import app_init


def test_get_email_service__dev(mocker: MockFixture):
    # given
    mocker.patch.object(APP_SETTINGS, "env", "dev")
    app = cast("Flask", "dummy_app")
    mocked_extensions = Mock()
    mocked_extensions.mail = Mock()
    mocked_extensions.mail.init_app = Mock()
    mocker.patch.object(
        word_games.extensions,
        "extensions_manager",
        mocked_extensions,
    )
    service_class = Mock()
    mocker.patch.object(
        word_games.email.smtp_adapter,
        "SMTPEmailService",
        service_class,
    )

    # when
    email_service = app_init.get_email_service(app)

    # then
    assert mocked_extensions.mail.init_app.call_count == 1
    assert mocked_extensions.mail.init_app.call_args == call(app)
    assert service_class.call_count == 1
    assert service_class.call_args == call(mocked_extensions.mail)
    assert email_service is service_class.return_value


def test_get_email_service__pro(mocker: MockFixture):
    # given
    mocker.patch.object(APP_SETTINGS, "env", "pro")
    app = Mock(spec=Flask)
    app.config = {"RESEND_KEY": "key"}
    service_class = Mock()
    mocker.patch.object(
        word_games.email.resend_adapter,
        "ResendEmailService",
        service_class,
    )

    # when
    email_service = app_init.get_email_service(app)

    # then
    assert service_class.call_count == 1
    assert service_class.call_args == call(api_key="key")
    assert email_service is service_class.return_value


@pytest.mark.parametrize("env", ["invalid_name", ""])
def test_get_email_service__invalid(mocker: MockFixture, env: str):
    # given
    mocker.patch.object(APP_SETTINGS, "env", env)
    app = Mock(spec=Flask)

    # when / then
    with pytest.raises(ValueError, match=f"Invalid environment: {env}"):
        app_init.get_email_service(app)
