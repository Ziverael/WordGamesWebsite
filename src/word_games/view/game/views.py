from . import game


@game.route("/play/<string:game_id>", methods=["GET", "POST"])
def play(game_id: str): ...
