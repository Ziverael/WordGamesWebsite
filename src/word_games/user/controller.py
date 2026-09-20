import uuid

from word_games.error import WordGamesError
from word_games.user.db import select_user_exists_with_public_id


def raise_if_user_not_exists(public_id: uuid.UUID) -> None:
    if not select_user_exists_with_public_id(public_id):
        msg = f"User with public id {public_id}"
        raise WordGamesError(msg)
