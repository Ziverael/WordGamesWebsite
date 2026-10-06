import uuid

from word_games.error import WordGamesError
from word_games.game import db as _db
from word_games.game.db import Game
from word_games.user.controller import get_public_id_by_id


def get_game_id_by_title_and_creator(title: str, user_id: int) -> uuid.UUID:
    if (
        game_id := _db.select_public_id_where_title_and_creator(title, user_id)
    ) is not None:
        return game_id
    msg = "Such game not exists."
    raise WordGamesError(msg)


def get_title_of_user_game_by_public_id(
    game_id: uuid.UUID, user_id: uuid.UUID
) -> str:
    try:
        raise_if_user_is_not_the_game_owner(
            user_public_id=user_id, game_id=game_id
        )
        raise_if_game_with_public_id_not_exists(game_id)
        title = _db.select_title_where_public_id(game_id)
    except Exception as e:
        msg = "Cannot get game title."
        raise WordGamesError(msg) from e
    else:
        return title


def raise_if_user_is_not_the_game_owner(
    user_public_id: uuid.UUID, game_id: uuid.UUID
) -> None:
    creator = _db.select_creator_where_public_id(game_id)
    creator_public_id = get_public_id_by_id(creator)
    if creator_public_id != user_public_id:
        msg = f"User {user_public_id} is not an owner of a this game."
        raise WordGamesError(msg)


def raise_if_game_with_public_id_not_exists(game_id: uuid.UUID) -> None:
    if not _db.exists_game_id(game_id):
        msg = f"Game with id {game_id} not exists."
        raise WordGamesError(msg)


__all__ = ["Game"]
