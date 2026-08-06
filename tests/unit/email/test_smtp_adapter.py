from typing import cast

from word_games.email import smtp_adapter


class TestSMTPEmailService:
    def test_init(self):
        # given
        mail = cast("str", "dummy_mail")

        # when
        service = smtp_adapter.SMTPEmailService(mail)

        # then
        assert isinstance(service, smtp_adapter.EmailService)
        assert service.mail == mail
