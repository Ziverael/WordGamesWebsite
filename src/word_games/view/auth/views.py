from fnmatch import fnmatch

from .forms import (
    ChangeEmailForm,
    ChangePasswordForm,
    LoginForm,
    PasswordResetForm,
    PasswordResetRequestForm,
    RegistrationForm,
)
from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from word_games.config.smtp import SMTP_SETTINGS
from word_games.db import get_session
from word_games.email.controller import send_email
from word_games.user.db import User
from word_games.view.auth import auth


ALLOWED_ENDPOINTS = [
    "auth.*",
    "static",
    "main.index",
]


def endpoint_allowed(endpoint):
    if endpoint is None:
        return False
    return any(fnmatch(endpoint, pattern) for pattern in ALLOWED_ENDPOINTS)


@auth.before_app_request
def before_request():
    if (
        current_user.is_authenticated
        and not current_user.confirmed
        and not endpoint_allowed(request.endpoint)
    ):
        return redirect(url_for("auth.unconfirmed"))
    return None


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Logging use next argument in URL to get back from logging page, to
    previously opened page. If next is not passed, by default user is redirected
    to index. However, if malicious actor passes different domain to next
    argument. Then this redirection will be ignored, and user will be redirected
    to the index.
    """
    form = LoginForm()
    if form.validate_on_submit():
        with get_session() as session:
            normed_email = form.email.data.lower()
            user = session.query(User).filter_by(email=normed_email).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_ = request.args.get("next")
            if next_ is None or not next_.startswith("/"):
                next_ = url_for("main.index")
            return redirect(next_)
        flash("Login failed.", "error")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            username=form.username.data,
            password=form.password.data,
            role=form.role.data,
        )
        with get_session() as session:
            session.add(user)
        token = user.generate_confirmation_token()
        send_email(
            recipients=[user.email],
            sender=SMTP_SETTINGS.default_sender,
            subject="Confirm Your Account",
            html_body=render_template(
                "auth/email/register.html",
                user=user,
                token=token,
            ),
        )
        flash("A confirmation email has been sent to you by email.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("You have confirmed your account. Thanks!", "success")
    else:
        flash("The confirmation link is invalid or has expired.", "error")
    return redirect(url_for("main.index"))


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        recipients=[current_user.email],
        sender=SMTP_SETTINGS.default_sender,
        subject="Confirm Your Account",
        html_body=render_template(
            "auth/email/register.html",
            user=current_user,
            token=token,
        ),
    )
    flash("A new confirmation email has been sent to you by email.", "info")
    return redirect(url_for("main.index"))


@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            with get_session() as session:
                session.add(current_user)
            flash("Your password has been updated.", "success")
            return redirect(url_for("main.index"))
        flash("Invalid password.", "error")
    return render_template("auth/change_password.html", form=form)


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        normed_email = form.email.data.lower()
        with get_session() as session:
            user = session.query(User).filter_by(email=normed_email).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                recipients=[current_user.email],
                sender=SMTP_SETTINGS.default_sender,
                subject="Reset Your Password",
                html_body=render_template(
                    "auth/email/reset_password.html",
                    user=current_user,
                    token=token,
                ),
            )
        flash(
            "An email with instructions to reset your password has been "
            "sent to you.",
            "info",
        )
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            flash("Your password has been updated.", "success")
            return redirect(url_for("auth.login"))
        return redirect(url_for("main.index"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/change_email", methods=["GET", "POST"])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(
                recipients=[new_email],
                sender=SMTP_SETTINGS.default_sender,
                subject="Reset Your Password",
                html_body=render_template(
                    "auth/email/change_password.html",
                    user=current_user,
                    token=token,
                    old_email=current_user.email,
                ),
            )
            flash(
                "An email with instructions to confirm your new email "
                "address has been sent to you.",
                "info",
            )
            return redirect(url_for("main.index"))
        flash("Invalid email or password.", "error")
    return render_template("auth/change_email.html", form=form)


@auth.route("/change_email/<token>")
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash("Your email address has been updated.", "success")
    else:
        flash("Invalid request.", "error")
    return redirect(url_for("main.index"))
