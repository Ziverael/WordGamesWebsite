import uuid

from . import profile
from flask import flash, redirect, render_template, url_for
from flask_login import current_user

from word_games.constants import HTTPStatusCode
from word_games.game.db import (
    delete_game_where_public_id,
    select_public_business_columns,
    select_title_where_public_id,
    select_user_games_public_ids,
)
from word_games.utils import normalize_text, rename_dict_key


@profile.route("/profile/me", methods=["GET", "POST"])
def user_profile():
    return render_template(
        "profile/me.html",
        user=current_user,
    ), HTTPStatusCode.OK


@profile.route("/profile/security", methods=["GET", "POST"])
def security():
    return render_template(
        "profile/security.html",
        user=current_user,
    ), HTTPStatusCode.OK


@profile.route("/profile/students", methods=["GET", "POST"])
def students():
    return render_template(
        "profile/students.html",
        user=current_user,
    ), HTTPStatusCode.OK


@profile.route("/profile/assignment", methods=["GET", "POST"])
def assignments():
    return render_template(
        "profile/assignments.html",
        user=current_user,
    ), HTTPStatusCode.OK


@profile.route("/profile/games", methods=["GET", "POST"])
def games():
    game_meta_table = select_public_business_columns(current_user.id)
    return render_template(
        "profile/games.html",
        user=current_user,
        table=game_meta_table,
    ), HTTPStatusCode.OK


def _clean_keys(dictionary: dict) -> None:
    for key in dictionary:
        rename_dict_key(dictionary, key, normalize_text(key))


@profile.route("/profile/games/delete/<uuid:game_id>")
def delete_game(game_id: uuid.UUID):
    user_games_ids = select_user_games_public_ids(current_user.id)
    if game_id not in user_games_ids:
        flash("Cannot perform this operation", "error")
    else:
        game_title = select_title_where_public_id(game_id)
        delete_game_where_public_id(game_id)
        flash(f"Game '{game_title}' successfully deleted.", "success")
    return redirect(url_for("profile.games"))


@profile.route("/profile/games/assign/<uuid:game_id>", methods=["GET", "POST"])
def assign_game(game_id: uuid.UUID): ...


@profile.route("/profile/game_editor", methods=["GET", "POST"])
def game_editor():
    return render_template(
        "profile/game_editor.html",
        user=current_user,
    ), HTTPStatusCode.OK
