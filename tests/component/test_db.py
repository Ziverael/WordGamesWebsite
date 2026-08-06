from flask import g
from sqlalchemy.orm import Session

from word_games import db


def test_get_session(app_context):
    # when
    with app_context:
        with db.get_session() as session:
            # then
            assert g.db_session == session
        assert isinstance(session, Session)
