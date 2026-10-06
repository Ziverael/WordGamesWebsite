from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, ValidationError
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


class ContactRemoveForm(FlaskForm):
    def __init__(self, contacts: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contact.choices = [(name, name) for name in contacts]

    contact = SelectField(
        "Contact Name", validators=[DataRequired()], choices=[]
    )
    submit = SubmitField("Remove contact")


class CreateAssignmentForm(FlaskForm):
    def __init__(self, students: list[str], games: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student.choices = [(name, name) for name in students]
        self.game.choices = [(title, title) for title in games]

    student = SelectField(
        "Student Name", validators=[DataRequired()], choices=[]
    )
    game = SelectField("Game Title", validators=[DataRequired()], choices=[])
    submit = SubmitField("Submit Invitation")


class RemoveAssignmentsForm(FlaskForm):
    def __init__(self, tasks: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task.choices = [(hrid, hrid) for hrid in tasks]

    task = SelectField("Task Name", validators=[DataRequired()], choices=[])
    submit = SubmitField("Remove Assignment")
