from contextlib import contextmanager
from functools import lru_cache

from flask import g
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from word_games.config.db import DATABASE_SETTINGS


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    engine: Engine = create_engine(
        url=DATABASE_SETTINGS.connection_string,
        pool_size=DATABASE_SETTINGS.pool_size,
        max_overflow=DATABASE_SETTINGS.max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    return engine


def create_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)


SessionFactory = create_session_factory(get_engine())


@contextmanager
def get_session():
    if "db_session" not in g:
        g.db_session = SessionFactory()
    try:
        yield g.db_session
        g.db_session.commit()
    except Exception:
        g.db_session.rollback()
        raise


def register_db_cleanup(app):
    @app.teardown_appcontext
    def cleanup(exception=None):
        session = g.pop("db_session", None)

        if session is None:
            return

        try:
            if exception is None:
                session.commit()
            else:
                session.rollback()
        finally:
            session.close()
