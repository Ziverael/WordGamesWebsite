import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from word_games.game.db import Game


class TestGame:
    def test_insert(self, db_session, game_factory):
        # given
        game = game_factory.build()

        # when
        db_session.add(game)
        db_session.commit()

        # then
        stmt = select(Game)
        games_in_db = db_session.scalars(stmt).all()
        assert len(games_in_db) == 1
        assert games_in_db[0] == game

    def test_unique_id(self, db_session, game_factory):
        # given
        game1 = game_factory.build(id=1)
        game2 = game_factory.build(id=1)

        # when
        db_session.add(game1)
        db_session.commit()
        db_session.add(game2)

        # then
        with pytest.raises(IntegrityError):
            db_session.commit()
