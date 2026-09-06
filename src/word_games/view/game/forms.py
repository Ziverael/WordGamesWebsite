from flask_wtf import FlaskForm
from wtforms import SubmitField


class GameSubmitForm(FlaskForm):
    submit = SubmitField("Submit")

    def disable_form(self):
        for field in self:
            if hasattr(field, "render_kw"):
                field.render_kw = field.render_kw or {}
                field.render_kw["disabled"] = True
