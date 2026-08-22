from itertools import chain

from flask import flash, redirect, render_template, url_for
from flask_login import current_user

from word_games.game.model import GAME_LAYOUTS
from word_games.model import Role
from word_games.view.game_editor import game_editor
from word_games.view.game_editor.forms import GameForm, GameSetupForm
from word_games.view.game_editor.game_validator import (
    ValidationError,
    load_json,
)


@game_editor.before_request
def before_request():
    if current_user.role != Role.teacher:
        flash("Game editor is not avaiable for your role.", "error")
        return redirect(url_for("main.index"))
    return None


@game_editor.route("/game_editor/main", methods=["GET", "POST"])
def main():
    return redirect(url_for("game_editor.setup"))


@game_editor.route("/game_editor/setup", methods=["GET", "POST"])
def setup():
    form = GameSetupForm()
    game_layouts_images = {
        name: url_for("static", filename=f"image/svg/{name}.svg")
        for name in list(chain(*GAME_LAYOUTS.values()))
    }
    if form.validate_on_submit():
        editor = f"{form.type.data}-{form.layout.data}"
        return redirect(url_for("game_editor.editor", editor=editor))
    return render_template(
        "game_editor/setup.html",
        form=form,
        layouts_mapping=GAME_LAYOUTS,
        layout_images=game_layouts_images,
    )


@game_editor.route("/game_editor/editor/<editor>", methods=["GET", "POST"])
def editor(editor: str):
    editor_page = f"game_editor/editors/{editor}.html"
    if not _is_valid_editor_page(editor_page):
        flash(f"{editor} is not a valid editor.", "error")
        return redirect(url_for("game_editor.setup"))
    editor_state: dict | None = None
    form = GameForm(editor_type=editor)
    if form.validate_on_submit():
        ...
    editor_state = _get_editor_state(form.content.data)

    return render_template(editor_page, form=form, editor_state=editor_state)


def _is_valid_editor_page(page: str) -> bool:
    page_root = "game_editor/editors"
    valid_pages = [
        f"{page_root}/{key}-{v}.html"
        for key, values in GAME_LAYOUTS.items()
        for v in values
    ]
    return page in valid_pages


def _get_editor_state(raw_editor_content: str | None):
    editor_state: dict | None = None
    try:
        if not getattr(raw_editor_content, "security_violation", False):
            editor_state = load_json(raw_editor_content)
    except ValidationError:
        ...
    else:
        return editor_state
