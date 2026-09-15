from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired

from word_games.user.db import select_user_exists_with_public_id


if TYPE_CHECKING:
    from wtforms import Field


class StudentInvitationForm(FlaskForm):
    student_id = StringField("Student Id", validators=[DataRequired()])
    submit = SubmitField("Submit Invitation")

    def validate_student_id(self, field: Field) -> None:
        try:
            user_uuid = uuid.UUID(field.data)
        except Exception as e:
            msg = f"{field.data} is not a valid student id."
            raise ValidationError(msg) from e
        else:
            if not select_user_exists_with_public_id(user_uuid):
                msg = f"User with public id {field.data} does not exists."
                raise ValidationError(msg)
