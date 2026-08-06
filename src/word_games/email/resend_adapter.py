import resend

from word_games.email.service import EmailService


class ResendEmailService(EmailService):
    def __init__(self, api_key):
        resend.api_key = api_key

    def send(
        self,
        *,
        subject,
        recipients,
        text_body,
        html_body,
        sender=None,
    ):

        resend.Emails.send(
            {
                "from": sender,
                "to": recipients,
                "subject": subject,
                "text": text_body,
                "html": html_body,
            }
        )
