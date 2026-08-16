from flask_wtf import FlaskForm
from wtforms import (
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    ValidationError,
)
from wtforms.validators import DataRequired

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
    submit = SubmitField("Save")
