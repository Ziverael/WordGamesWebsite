from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from word_games.database import BaseTable


class Task(BaseTable):
    """Task is a declaration of assignment the Game for a user. Teacher can
    assigns a game to a student. There can be multiple tasks pointing the same
    game.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int]
    assignee_id: Mapped[int]
    created_at: Mapped[datetime]
    viewed_at: Mapped[datetime | None]
    recently_viewed_at: Mapped[datetime | None]
