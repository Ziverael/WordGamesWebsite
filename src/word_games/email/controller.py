from flask import current_app


def send_email(
    *,
    subject: str,
    recipients: list[str],
    text_body: str | None = None,
    html_body: str | None = None,
    sender: str | None = None,
) -> None:
    if text_body is None and html_body is None:
        msg = "At least one of text_body or html_body must be provided."
        raise ValueError(msg)
    text = text_body or ""
    html = html_body or ""
    current_app.extensions["email_service"].send(
        subject=subject,
        recipients=recipients,
        text_body=text,
        html_body=html,
        sender=sender,
    )
