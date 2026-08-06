from typing import cast
from unittest.mock import Mock

import pytest
from flask import Flask
from pytest_mock import MockFixture

from word_games.email import controller


def test_send_email__missing_body():
    # given
    sub = cast("str", "subject")
    rec = cast("list[str]", "recipients")
    text = None
    html = None
    sender = cast("str", "sender")

    # when / then
    with pytest.raises(
        ValueError,
        match=r"At least one of text_body or html_body must be provided.",
    ):
        controller.send_email(
            subject=sub,
            recipients=rec,
            text_body=text,
            html_body=html,
            sender=sender,
        )


def test_send_email__missing_body_default():
    # given
    sub = cast("str", "subject")
    rec = cast("list[str]", "recipients")
    sender = cast("str", "sender")

    # when / then
    with pytest.raises(
        ValueError,
        match=r"At least one of text_body or html_body must be provided.",
    ):
        controller.send_email(
            subject=sub,
            recipients=rec,
            sender=sender,
        )


@pytest.mark.parametrize(
    ("text", "html"),
    [(None, "html body"), ("text body", None), ("text body", "html body")],
)
def test_send_email(mocker: MockFixture, text: str | None, html: str | None):
    # given
    sub = cast("str", "subject")
    rec = cast("list[str]", "recipients")
    text = text or ""
    html = html or ""
    sender = cast("str", "sender")
    app = Mock(spec=Flask)
    send_mock = Mock()
    email_service = Mock()
    email_service.send = send_mock
    app.extensions = {"email_service": email_service}
    mocker.patch.object(controller, "current_app", app)

    # when
    controller.send_email(
        subject=sub,
        recipients=rec,
        text_body=text,
        html_body=html,
        sender=sender,
    )

    # then
    assert send_mock.call_count == 1
