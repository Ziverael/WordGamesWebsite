from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

from word_games.user.db import User


class LoginForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or "
                "underscores",
            ),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("password_check", message="Passwords must match."),
        ],
    )
    password_check = PasswordField(
        "Confirm password", validators=[DataRequired()]
    )
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            msg = "Email already registered."
            raise ValidationError(msg)

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            msg = "Username already in use."
            raise ValidationError(msg)


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[DataRequired()])
    password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            EqualTo("password_new", message="Passwords must match."),
        ],
    )
    password_enw = PasswordField(
        "Confirm new password", validators=[DataRequired()]
    )
    submit = SubmitField("Update Password")

    def validate_new_password(self, field):
        if field.data == self.old_password.data:
            msg = "New password must be different from old password."
            raise ValidationError(msg)


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    submit = SubmitField("Reset Password")


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            EqualTo("password_new", message="Passwords must match"),
        ],
    )
    password_new = PasswordField(
        "Confirm password", validators=[DataRequired()]
    )
    submit = SubmitField("Reset Password")


class ChangeEmailForm(FlaskForm):
    email = StringField(
        "New Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Update Email Address")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            msg = "Email already registered."
            raise ValidationError(msg)
