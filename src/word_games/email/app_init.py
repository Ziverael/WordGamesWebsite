# ruff: noqa: PLC0415
from typing import TYPE_CHECKING

from flask import Flask

from word_games.config.app import APP_SETTINGS


if TYPE_CHECKING:
    from word_games.email.service import EmailService


def get_email_service(app: Flask):
    email_service: EmailService
    match env := APP_SETTINGS.env:
        case "dev":
            from word_games.email.smtp_adapter import SMTPEmailService
            from word_games.extensions import extensions_manager

            extensions_manager.mail.init_app(app)
            email_service = SMTPEmailService(extensions_manager.mail)
        case "pro":
            from word_games.email.resend_adapter import ResendEmailService

            email_service = ResendEmailService(api_key=app.config["RESEND_KEY"])
        case _:
            msg = f"Invalid environment: {env}"
            raise ValueError(msg)
    return email_service
