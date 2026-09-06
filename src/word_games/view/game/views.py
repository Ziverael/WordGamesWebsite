import uuid

from . import game
from flask import flash, redirect, render_template, request, url_for

from word_games.game.db import (
    select_content_where_public_id,
    select_precise_category_where_public_id,
    select_title_where_public_id,
)
from word_games.view.game.forms import GameSubmitForm
from word_games.view.game.utils import FillGapsSentences


@game.route("/play/<uuid:game_id>", methods=["GET", "POST"])
def play(game_id: uuid.UUID):
    category = select_precise_category_where_public_id(game_id=game_id)
    if category is None:
        flash("Cannot find game data.", "error")
        return redirect(url_for("main.index"))
    type_, subtype = category
    template = f"{type_}-{subtype}"
    title = select_title_where_public_id(game_id)
    content = select_content_where_public_id(game_id)
    if content is None:
        flash("Cannot load this game", "error")
        return redirect(url_for("main.index"))
    form = GameSubmitForm()
    if form.validate_on_submit():
        grader = Grader(game_type=template)
        submitted_form = request.form.to_dict()
        submitted_form.pop("csrf_token")
        submitted_form.pop("submit")
        compared = grader.display_correct_answers(submitted_form, content)
        score = grader.grade(compared)
        form.disable_form()
        results = {"matches": compared, "score": score}
    else:
        results = None
    game_challange = setup_game(template=template, content=content)
    return render_template(
        f"game/{template}.html",
        form=form,
        title=title,
        content=game_challange,
        results=results,
    )


def setup_game(template: str, content: dict):
    match template:
        case "fill_gaps-sentences":
            return get_sentences_with_gaps(content)
        case _:
            msg = "Invalid game type"
            raise ValueError(msg)


def get_sentences_with_gaps(content: dict):
    output: list[str] = []
    copied_content = content.copy()
    for sentence_idx, (sentence, gaps) in enumerate(copied_content.items()):
        for rev_gap_idx, gap in enumerate(
            sorted(gaps, key=lambda x: x["start"], reverse=True)
        ):
            gap_idx = len(gaps) - rev_gap_idx - 1
            start = gap["start"]
            end = gap["end"]
            output_sentence = (
                sentence[:start]
                + f"**{sentence_idx}.{gap_idx}**"
                + sentence[end + 1 :]
            )
        output.append(output_sentence)
    return output


class Grader:
    def __init__(self, game_type: str) -> None:
        self.game_type = game_type

    def display_correct_answers(
        self, form, content
    ) -> dict[str, dict[str, str]]:
        match self.game_type:
            case "fill_gaps-sentences":
                return FillGapsSentences.pair_responces_with_answers(
                    response=form, content=content
                )
            case _:
                msg = "Invalid game type"
                raise ValueError(msg)

    def grade(self, answers: dict[str, dict[str, str]]):
        match self.game_type:
            case "fill_gaps-sentences":
                return FillGapsSentences.grade(answers=answers)

    def send_response(self, answers: dict[str, dict[str, str]]) -> None:
        match self.game_type:
            case "fill_gaps-sentences":
                return FillGapsSentences.send_response(answers=answers)
