"""This file holds all database tables that should be managed by Alembic.

Don't import anything from this file.
"""
# ruff: noqa: F401

from word_games.game.db import Game
from word_games.task.db import Task
from word_games.user.db import User
