from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    HiddenField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    ValidationError,
)
from wtforms.validators import DataRequired

import word_games.view.game_editor.game_validator as game_validators
from word_games.error import SecurityViolationError
from word_games.game.db import select_user_games_titles
from word_games.game.model import GAME_LAYOUTS, GameType


class GameSetupForm(FlaskForm):
    type = SelectField(
        "Game Type",
        choices=[(t.value, t.name.replace("_", " ").title()) for t in GameType],
        validate_choice=True,
        validators=[DataRequired()],
    )
    layout = RadioField(
        "Game Layout",
        choices=[],
        validate_choice=False,
        validators=[DataRequired()],
    )
    submit = SubmitField("Next")

    def validate_layout(self, field):
        """Because we generate this list dynamically, we transfer
        choice validation to this custom function.
        """
        valid_layouts = GAME_LAYOUTS.get(self.type.data, None)
        if valid_layouts is None:
            msg = "Invalid game type."
            raise ValidationError(msg)
        if field.data not in valid_layouts:
            msg = "This layout is not available for the selected game type."
            raise ValidationError(msg)


class GameForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    content = HiddenField("Content")
    submit = SubmitField("Save")

    def __init__(self, editor_type: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editor_type = editor_type
        self.game_type, self.game_subtype = editor_type.split("-")
        self._security_violation = False
        self.edit_mode = False

    def toogle_edit_mode(self) -> None:
        self.edit_mode = True

    def remove_security_violation_flag(self) -> None:
        self._security_violation = False

    def validate_content(self, field):
        """this is extremely one validation spot. Because JS code which produces
        game is on client side, one may still modify this code in the fly
        in order to generate malicious code and try to infest the server.

        In that case we have to treat this field as extremely unsafe and
        analyze if input exactly what we expects."""
        try:
            match self.editor_type:
                case "fill_gaps-sentences":
                    game_validators.fill_gaps_sentences(field.data)
                case _:
                    msg = f"Invalid pair: {self.editor_type}"
                    raise ValidationError(msg)
        except SecurityViolationError as e:
            self._security_violation = True
            raise ValidationError(str(e)) from e

    def validate_name(self, field):
        user_game_titles = select_user_games_titles(current_user.id)
        if field.data in user_game_titles and not self.edit_mode:
            msg = "You have a game with this title."
            raise ValidationError(msg)
