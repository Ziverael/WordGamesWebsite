from abc import ABC, abstractmethod


class EmailService(ABC):
    @abstractmethod
    def send(
        self,
        *,
        subject: str,
        recipients: list[str],
        text_body: str,
        html_body: str,
        sender: str | None = None,
    ): ...
