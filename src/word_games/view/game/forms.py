from flask_wtf import FlaskForm
from wtforms import SubmitField


class GameSubmitForm(FlaskForm):
    submit = SubmitField("Submit")
