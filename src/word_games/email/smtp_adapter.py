from typing import TYPE_CHECKING

from flask_mail import Message

from word_games.email.service import EmailService


if TYPE_CHECKING:
    from flask_mail import Mail


class SMTPEmailService(EmailService):
    def __init__(self, mail: "Mail"):
        self.mail = mail

    def send(
        self,
        *,
        subject,
        recipients,
        text_body,
        html_body,
        sender=None,
    ):
        msg = Message(
            subject=subject,
            sender=sender,
            recipients=recipients,
        )
        msg.body = text_body
        msg.html = html_body
        self.mail.send(msg)
