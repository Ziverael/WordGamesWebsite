import uuid

from . import game
from flask import flash, redirect, render_template, url_for

from word_games.game.db import (
    select_title_where_public_id,
    select_type_subtype_and_content_where_public_id,
)
from word_games.view.game.forms import GameSubmitForm


@game.route("/play/<uuid:game_id>", methods=["GET", "POST"])
def play(game_id: uuid.UUID):
    game_spec = select_type_subtype_and_content_where_public_id(game_id)
    if game_spec is None:
        flash("Cannot find game data.", "error")
        return redirect(url_for("main.index"))
    type_, subtype, content = game_spec
    template = f"{type_}-{subtype}"
    title = select_title_where_public_id(game_id)
    form = GameSubmitForm()
    if form.validate_on_submit():
        ...
    return render_template(
        f"game/{template}.html",
        form=form,
        title=title,
        content=content,
    )
