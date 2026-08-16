from flask import Blueprint


game_editor = Blueprint("game_editor", __name__)

from . import views as views
