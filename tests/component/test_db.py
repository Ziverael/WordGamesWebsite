from flask import g
from sqlalchemy.orm import Session

from word_games import db


def test_get_session(app_context):
    # when
    with app_context:
        results = db.get_session()

        # then
        assert g.db_session == results
    assert isinstance(results, Session)
