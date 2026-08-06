from datetime import datetime

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from word_games.database import BaseTable


class Game(BaseTable):
    """Is a set of challenges defined for a given game template. The game can
    be created by teacher. Object of game is created via game factory.

    Args:
        BaseTable (_type_): _description_
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    created_at: Mapped[datetime]
    creator: Mapped[int]
    content: Mapped[dict] = mapped_column(JSON)
