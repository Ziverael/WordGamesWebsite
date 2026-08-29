from . import main
from flask import render_template

from word_games.constants import HTTPStatusCode


@main.route("/", methods=["GET", "POST"])
def index():
    return render_template(
        "index.html",
    ), HTTPStatusCode.OK
