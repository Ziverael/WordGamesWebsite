import time
from datetime import datetime

import requests
from flask import Flask
from flask_mail import Mail
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from word_games.config.smtp import SMTP_SETTINGS
from word_games.email.smtp_adapter import SMTPEmailService


class MailApi(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SMTP_", extra="ignore")

    server: str = Field(min_length=1)
    web_ui: int
    wait_time: float = Field(default=0.2)

    @property
    def messages_api(self) -> str:
        return f"http://{self.server}:{self.web_ui}/api/v1/messages"


MAILPIT_API = MailApi()


def wait_for_mail(timeout=5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(MAILPIT_API.messages_api, timeout=5.0)
        r.raise_for_status()
        messages = r.json()["messages"]
        if messages:
            return messages
        time.sleep(MAILPIT_API.wait_time)
    msg = "No mail received"
    raise AssertionError(msg)


class TestSMTPEmailService:
    def test_send(self):
        """Caution: we need to use new app instance, because if we use fixture `app`,
        then we get full initialization with already registered mail service ,etc.
        """
        # given
        app = Flask("test_app")
        mail = Mail()
        app.config.update(**SMTP_SETTINGS.model_dump(by_alias=True))
        mail.init_app(app)
        client = SMTPEmailService(mail=mail)
        sub = "Topic"
        rec = ["Anna@test.com", "Eren@test.com"]
        sec_acceptance_threshold = 5.0
        ts = time.time()

        # when
        client.send(
            subject=sub,
            recipients=rec,
            text_body="Welcome on the island",
            html_body="<section>Welcome on the island</section>",
            sender="me@test.com",
        )
        messages = wait_for_mail()
        msg = messages[0]

        # then
        msg_time = datetime.strptime(msg["Created"], "%Y-%m-%dT%H:%M:%S.%fZ")  # noqa: DTZ007
        assert msg_time.timestamp() < ts + sec_acceptance_threshold
        assert msg["Subject"] == "Topic"
        assert msg["From"]["Address"] == "me@test.com"
        exact_rec = sorted(user["Address"] for user in msg["To"])
        assert exact_rec == sorted(rec)
