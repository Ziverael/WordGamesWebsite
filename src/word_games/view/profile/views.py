from . import profile
from flask import render_template
from flask_login import current_user

from word_games.constants import HTTPStatusCode


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
    return render_template(
        "profile/games.html",
        user=current_user,
    ), HTTPStatusCode.OK


@profile.route("/profile/game_editor", methods=["GET", "POST"])
def game_editor():
    return render_template(
        "profile/game_editor.html",
        user=current_user,
    ), HTTPStatusCode.OK
