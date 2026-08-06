import re

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    ValidationError,
)
from wtforms.validators import DataRequired, Email, EqualTo, Regexp

from word_games.constants import EMAIL_LENGTH, PASSWORD_LENGTH, USERNAME_LENGTH
from word_games.db import get_session
from word_games.model import Role
from word_games.user.db import User


def check_password_complexity(_form, field):
    password = field.data
    rules = [
        (
            len(password) >= PASSWORD_LENGTH.min,
            "Password must be at least 12 characters long.",
        ),
        (
            re.search(r"[A-Z]", password),
            "Password must contain an uppercase letter.",
        ),
        (
            re.search(r"[a-z]", password),
            "Password must contain a lowercase letter.",
        ),
        (re.search(r"\d", password), "Password must contain a number."),
        (
            re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\/~`]", password),
            "Password must contain a special character.",
        ),
        (" " not in password, "Password cannot contain spaces."),
    ]

    for condition, message in rules:
        if not condition:
            raise ValidationError(message)


class LoginForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), EMAIL_LENGTH, Email()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), EMAIL_LENGTH, Email()]
    )
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            USERNAME_LENGTH,
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or "
                "underscores",
            ),
        ],
    )
    role = SelectField(
        "Role",
        choices=[(r.name, r.name.capitalize()) for r in Role],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            PASSWORD_LENGTH,
            check_password_complexity,
            EqualTo("password_check", message="Passwords must match."),
        ],
    )
    password_check = PasswordField(
        "Confirm password", validators=[DataRequired()]
    )
    submit = SubmitField("Register")

    def validate_email(self, field):
        with get_session() as session:
            normed_email = field.data.lower()
            if session.query(User).filter_by(email=normed_email).first():
                msg = "Email already registered."
                raise ValidationError(msg)

    def validate_username(self, field):
        with get_session() as session:
            if session.query(User).filter_by(username=field.data).first():
                msg = "Username already in use."
                raise ValidationError(msg)


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[DataRequired()])
    password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            PASSWORD_LENGTH,
            check_password_complexity,
            EqualTo("password_new", message="Passwords must match."),
        ],
    )
    password_new = PasswordField(
        "Confirm new password", validators=[DataRequired()]
    )
    submit = SubmitField("Update Password")

    def validate_password_new(self, field):
        if field.data == self.old_password.data:
            msg = "New password must be different from old password."
            raise ValidationError(msg)

    def validate_old_password(self, field):
        with get_session() as session:
            db_user = (
                session.query(User)
                .filter_by(username=current_user.username)
                .first()
            )
            if not db_user.verify_password(field.data):
                msg = "Old password do not match."
                raise ValidationError(msg)


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), EMAIL_LENGTH, Email()]
    )
    submit = SubmitField("Reset Password")


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            PASSWORD_LENGTH,
            check_password_complexity,
            EqualTo("password_new", message="Passwords must match."),
        ],
    )
    password_new = PasswordField(
        "Confirm password", validators=[DataRequired()]
    )
    submit = SubmitField("Reset Password")


class ChangeEmailForm(FlaskForm):
    email = StringField(
        "New Email", validators=[DataRequired(), EMAIL_LENGTH, Email()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Update Email Address")

    def validate_email(self, field):
        normed_email = field.data.lower()
        if current_user.email.lower() == normed_email:
            msg = "New email should not be the current email."
            raise ValidationError(msg)
        with get_session() as session:
            if session.query(User).filter_by(email=normed_email).first():
                msg = "Such email is already registered."
                raise ValidationError(msg)

    def validate_password(self, field):
        with get_session() as session:
            db_user = (
                session.query(User)
                .filter_by(username=current_user.username)
                .first()
            )
            if not db_user.verify_password(field.data):
                msg = "Password is invalid."
                raise ValidationError(msg)
