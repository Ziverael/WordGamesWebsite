from datetime import datetime

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from word_games.database import BaseTable


class GameTable(BaseTable):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    created_at: Mapped[datetime]
    creator: Mapped[int]
    content: Mapped[dict] = mapped_column(JSON)


class TaskTable(BaseTable):
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int]
    assignee_id: Mapped[int]
    created_at: Mapped[datetime]
    viewed_at: Mapped[datetime | None]
    recently_viewed_at: Mapped[datetime | None]
