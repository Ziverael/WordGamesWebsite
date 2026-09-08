import uuid
from datetime import datetime
from itertools import chain

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from word_games.db import get_session
from word_games.game.db import (
    Game,
    select_content_where_public_id,
    select_precise_category_where_public_id,
    select_title_where_public_id,
    update_game_content_where_creator_and_public_id,
    update_game_modified_at_where_creator_and_public_id,
    update_game_title_where_creator_and_public_id,
)
from word_games.game.model import (
    GAME_LAYOUTS,
    GameRepresentation,
    GameUpdate,
    GameUserScopeIdentifier,
)
from word_games.model import Role
from word_games.utils import TZ_UTC
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
    form = GameForm(editor_type=editor)
    editor_state: dict | None = None
    if (raw_game_id := request.args.get("game_id")) is not None:
        game_id = get_uuid(raw_game_id)
        game_repr = _load_game_representation(game_id)
        if game_repr is None:
            flash("Cannot find game data.", "error")
            return redirect(url_for("game_editor.setup"))
        form.toogle_edit_mode()
        form.set_original_name(game_repr.title)
        form.name.data = form.name.data or game_repr.title
        editor_state = _get_editor_state(form.content.data) or game_repr.content
    if form.validate_on_submit():
        parsed_content = load_json(form.content.data)
        if form.edit_mode:
            if game_id is None:
                abort(400, "game_id is missing")
            update = GameUpdate(
                title=form.name.data,
                content=parsed_content,
                modified_at=datetime.now(tz=TZ_UTC),
            )
            identifier = GameUserScopeIdentifier(
                creator=current_user.id, public_id=game_id
            )
            _update_game(update, identifier)
        else:
            game = Game(
                title=form.name.data,
                type=form.game_type,
                subtype=form.game_subtype,
                created_at=datetime.now(tz=TZ_UTC),
                creator=current_user.id,
                content=parsed_content,
            )
            _insert_game(game)
        return redirect(url_for("profile.games"))
    return render_template(editor_page, form=form, editor_state=editor_state)


@game_editor.route("/game_editor/edit/<uuid:game_id>", methods=["GET", "POST"])
def edit(game_id: uuid.UUID):
    precise_category = select_precise_category_where_public_id(game_id)
    if precise_category is None:
        flash("Cannot find game data.", "error")
        return redirect(url_for("profile.games"))
    type_, subtype = precise_category
    editor = f"{type_}-{subtype}"
    return redirect(
        url_for("game_editor.editor", editor=editor, game_id=game_id)
    )


def _load_game_representation(game_id: uuid.UUID) -> GameRepresentation | None:
    title = select_title_where_public_id(game_id)
    if title is None:
        current_app.logger.warning(
            "Cannot find game with %s for user %s{game_id}.",
            game_id,
            current_user.public_id,
        )
        return None
    content = select_content_where_public_id(game_id)
    return GameRepresentation(title=title, content=content)


def _insert_game(game: Game) -> None:
    try:
        with get_session() as session:
            session.add(game)
        flash("Game saved successfully", "success")
    except IntegrityError:
        flash(
            "Cannot write this game, because it violates integrity restrictions.",
            "error",
        )


def _update_game(
    update: GameUpdate, identifier: GameUserScopeIdentifier
) -> None:
    try:
        if update.title is not None:
            update_game_title_where_creator_and_public_id(
                update.title, identifier.creator, identifier.public_id
            )
        update_game_content_where_creator_and_public_id(
            update.content, identifier.creator, identifier.public_id
        )
        update_game_modified_at_where_creator_and_public_id(
            update.modified_at, identifier.creator, identifier.public_id
        )
        flash("Game updated successfully.", "success")
    except IntegrityError:
        flash(
            "Cannot write this game, because it violates integrity restrictions.",
            "error",
        )


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


def get_uuid(value: str) -> uuid.UUID:
    try:
        output = uuid.UUID(value)
    except (ValueError, TypeError):
        abort(400, "Invalid game_id")
    else:
        return output
