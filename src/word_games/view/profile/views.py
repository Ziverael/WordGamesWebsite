import uuid
from functools import wraps

from . import profile
from flask import flash, redirect, render_template, url_for
from flask_login import current_user

from word_games.constants import HTTPStatusCode
from word_games.error import WordGamesError
from word_games.game.db import (
    delete_game_where_public_id,
    select_public_business_columns,
    select_title_where_public_id,
    select_user_games_public_ids,
    select_user_games_titles,
)
from word_games.invitation.controller import send_invitation, get_user_accepted_invitations, get_user_pending_invitaitons, accept_invitation, reject_invitation
from word_games.user.db import select_neighbours_of_user_where_public_id, select_username_where_public_id
from word_games.utils import TZ_UTC, normalize_text, rename_dict_key
from word_games.view.hooks import admit_teacher, admit_student
from word_games.view.profile.forms import StudentInvitationForm


def requires_teacher_role(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if redirect_target := admit_teacher(
            msg="This subpage is not avaiable for your role."
        ):
            return redirect_target
        return f(*args, **kwargs)

    return wrapper

def requires_student_role(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if redirect_target := admit_student(
            msg="This subpage is not avaiable for your role."
        ):
            return redirect_target
        return f(*args, **kwargs)

    return wrapper

@profile.route("/profile/me", methods=["GET", "POST"])
def user_profile():
    return render_template(
        "profile/me.html",
        user=current_user,
    ), HTTPStatusCode.OK


@profile.route("/profile/security", methods=["GET", "POST"])
def security():
    return render_template(
        "profile/security.html",
        user=current_user,
    ), HTTPStatusCode.OK


@profile.route("/profile/students", methods=["GET", "POST"])
@requires_teacher_role
def students():
    return render_template(
        "profile/students.html",
        user=current_user,
    ), HTTPStatusCode.OK


@profile.route("/profile/student_invitation", methods=["GET", "POST"])
@requires_teacher_role
def student_invitation():
    form = StudentInvitationForm()
    if form.validate_on_submit():
        try:
            send_invitation(current_user.public_id, form.student_id.data)
            flash("Invitation submitted.", "success")
        except WordGamesError:
            flash(
                "Invitation already submitted and waiting for receiver confirmation.",
                "error",
            )
        finally:
            return redirect(url_for("main.index"))  # noqa: B012
    return render_template(
        "profile/invite_student.html",
        form=form,
    ), HTTPStatusCode.OK


@profile.route("/profile/teachers", methods=["GET", "POST"])
@requires_student_role
def teachers():
    teachers = get_user_accepted_invitations(current_user.public_id)
    invitations = get_user_pending_invitaitons(current_user.public_id)
    invitations_table = [
        {
            "invitation_id": inv.public_id,
            "teacher": select_username_where_public_id(inv.sender_id),
            "send_date": inv.send_date,
        } for inv in invitations
    ]
    flash(invitations_table)
    return render_template(
        "profile/teachers.html",
        user=current_user,
        teachers=teachers,
        invitations=invitations_table,
    ), HTTPStatusCode.OK

@profile.route("/profile/teachers/accept/<uuid:invitation_id>", methods=["GET", "POST"])
@requires_student_role
def accept_teacher_invitation(invitation_id: uuid.UUID):
    try:
        accept_invitation(invitation_id)
        flash(f"Invitation accepted.", "success")
    except WordGamesError:
        flash(f"Encountered problem while accepting invitation", "success")
    return redirect(url_for("profile.teachers"))

@profile.route("/profile/teachers/reject/<uuid:invitation_id>", methods=["GET", "POST"])
@requires_student_role
def reject_teacher_invitation(invitation_id: uuid.UUID):
    try:
        reject_invitation(invitation_id)
        flash(f"Invitation rejected.", "success")
    except WordGamesError:
        flash(f"Encountered problem while rejecting invitation", "success")
    return redirect(url_for("profile.teachers"))




@profile.route("/profile/assignment", methods=["GET", "POST"])
def assignments():
    return render_template(
        "profile/assignments.html",
        user=current_user,
    ), HTTPStatusCode.OK


@profile.route("/profile/games", methods=["GET", "POST"])
def games():
    game_meta_table = select_public_business_columns(current_user.id)
    return render_template(
        "profile/games.html",
        user=current_user,
        table=game_meta_table,
    ), HTTPStatusCode.OK


def _clean_keys(dictionary: dict) -> None:
    for key in dictionary:
        rename_dict_key(dictionary, key, normalize_text(key))


@profile.route("/profile/games/delete/<uuid:game_id>")
def delete_game(game_id: uuid.UUID):
    user_games_ids = select_user_games_public_ids(current_user.id)
    if game_id not in user_games_ids:
        flash("Cannot perform this operation", "error")
    else:
        game_title = select_title_where_public_id(game_id)
        delete_game_where_public_id(game_id)
        flash(f"Game '{game_title}' successfully deleted.", "success")
    return redirect(url_for("profile.games"))


@profile.route("/profile/games/assign/<uuid:game_id>", methods=["GET", "POST"])
def assign_game(game_id: uuid.UUID): ...


@profile.route("/profile/games/assign/", methods=["GET", "POST"])
def create_assignment():
    user_id = current_user.id
    available_games = select_user_games_titles(user_id=user_id)
    available_students = select_neighbours_of_user_where_public_id(
        public_id=user_id
    )
    return render_template(
        "profile/create_assignment.html",
        stuednts=available_students,
        games=available_games,
    ), HTTPStatusCode.OK


@profile.route("/profile/game_editor", methods=["GET", "POST"])
def game_editor():
    return render_template(
        "profile/game_editor.html",
        user=current_user,
    ), HTTPStatusCode.OK


@profile.app_template_filter("format_datetime")
def format_datetime(dt):
    if dt is None:
        return ""
    output = dt.replace(tzinfo=TZ_UTC)
    return output.isoformat()
