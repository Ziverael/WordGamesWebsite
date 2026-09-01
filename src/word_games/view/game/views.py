import uuid

from . import game


@game.route("/play/<uuid:game_id>", methods=["GET", "POST"])
def play(game_id: uuid.UUID): ...
