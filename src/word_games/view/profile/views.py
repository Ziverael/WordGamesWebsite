import uuid
from datetime import datetime
from functools import wraps

from . import profile
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user

from word_games.constants import HTTPStatusCode
from word_games.error import WordGamesError
from word_games.game.controller import (
    get_game_id_by_title_and_creator,
    get_title_of_user_game_by_public_id,
)
from word_games.game.db import (
    delete_game_where_public_id,
    select_public_business_columns,
    select_title_where_public_id,
    select_user_games_public_ids,
    select_user_games_titles,
)
from word_games.invitation.controller import (
    accept_invitation,
    cancel_invitation,
    reject_invitation,
    send_invitation,
)
from word_games.model import Role
from word_games.task.controller import add_task_to_db, delete_task_from_db
from word_games.user.controller import (
    delete_cn_relation_in_db,
    get_user_id_by_username,
    get_user_teachers_and_students_public_ids,
    get_username_by_public_id,
)
from word_games.user.db import (
    select_username_where_public_id,
)
from word_games.utils import TZ_UTC, normalize_text, rename_dict_key
from word_games.view.hooks import admit_teacher
from word_games.view.profile.forms import (
    ContactRemoveForm,
    CreateAssignmentForm,
    RemoveAssignmentsForm,
    StudentInvitationForm,
)
from word_games.view.profile.queries import (
    count_solved_tasks_where_assignee_and_creator,
    count_tasks_where_assignee_and_creator,
    select_task_description_where_assignee,
    select_task_description_where_assignee_and_creator,
    select_task_description_where_creator,
    select_task_natural_identifier_where_creator,
)


def requires_teacher_role(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if redirect_target := admit_teacher(
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


@profile.route("/profile/remove_student", methods=["GET", "POST"])
@requires_teacher_role
def remove_student():
    _, students = get_user_teachers_and_students_public_ids(
        public_id=current_user.public_id
    )
    students_names = [get_username_by_public_id(id_) for id_ in students]
    form = ContactRemoveForm(contacts=students_names)
    if form.validate_on_submit():
        student_id = get_user_id_by_username(form.contact.data)
        return redirect(
            url_for("profile.delete_relation", public_id=student_id)
        )
    return render_template(
        "profile/remove_student.html",
        form=form,
    ), HTTPStatusCode.OK


@profile.route("/profile/community", methods=["GET", "POST"])
def community():
    teachers, students = get_user_teachers_and_students_public_ids(
        current_user.public_id
    )
    teacher_table = [
        {
            "name": select_username_where_public_id(id_),
            "public_id": id_,
        }
        for id_ in teachers
    ]

    students_table = [
        {
            "name": select_username_where_public_id(id_),
            "public_id": id_,
            "assignments_count": (
                all_tasks := count_tasks_where_assignee_and_creator(
                    assignee=id_, creator=current_user.public_id
                )
            ),
            "solved_assignments_count": (
                solved_tasks := count_solved_tasks_where_assignee_and_creator(
                    assignee=id_, creator=current_user.public_id
                )
            ),
            "not_solved_assignments_count": all_tasks - solved_tasks,
        }
        for id_ in students
    ]
    return render_template(
        "profile/community.html",
        user=current_user,
        teachers=teacher_table,
        students=students_table,
    ), HTTPStatusCode.OK


@profile.route("/profile/community/delete/<uuid:public_id>")
def delete_relation(public_id: uuid.UUID):
    try:
        if current_user.role == Role.teacher:
            delete_cn_relation_in_db(
                teacher=current_user.public_id, student=public_id
            )
        else:
            delete_cn_relation_in_db(
                teacher=public_id, student=current_user.public_id
            )
        flash("Relation deleted.", "success")
    except WordGamesError:
        flash("Encountered problem during relation removin process", "failed")
    return redirect(url_for("profile.community"))


@profile.route("/profile/invitations", methods=["GET", "POST"])
def invitations():
    invitations_table = [
        {
            "invitation_id": inv.public_id,
            "teacher": select_username_where_public_id(inv.sender_id),
            "send_date": inv.send_date,
        }
        for inv in invitations
    ]
    flash(invitations_table)
    return render_template(
        "profile/teachers.html",
        user=current_user,
        invitations=invitations_table,
    ), HTTPStatusCode.OK


@profile.route(
    "/profile/community/accept/<uuid:invitation_id>", methods=["GET", "POST"]
)
def accept_teacher_invitation(invitation_id: uuid.UUID):
    try:
        accept_invitation(invitation_id)
        flash("Invitation accepted.", "success")
    except WordGamesError:
        flash("Encountered problem while accepting invitation", "success")
    return redirect(url_for("profile.community"))


@profile.route(
    "/profile/community/reject/<uuid:invitation_id>", methods=["GET", "POST"]
)
def reject_teacher_invitation(invitation_id: uuid.UUID):
    try:
        reject_invitation(invitation_id)
        flash("Invitation rejected.", "success")
    except WordGamesError:
        flash("Encountered problem while rejecting invitation", "success")
    return redirect(url_for("profile.community"))


@profile.route(
    "/profile/community/invitations/<uuid:invitation_id>",
    methods=["GET", "POST"],
)
@requires_teacher_role
def cancel_your_invitation(invitation_id: uuid.UUID):
    try:
        cancel_invitation(invitation_id)
        flash("Invitation rejected.", "success")
    except WordGamesError:
        flash("Encountered problem while rejecting invitation", "success")
    return redirect(url_for("profile.community"))


@profile.route("/profile/assignment", methods=["GET", "POST"])
def assignments():
    if (student := request.args.get("student_id")) is not None:
        got_tasks = []
        created_tasks = select_task_description_where_assignee_and_creator(
            student, current_user.public_id
        )
    elif (teacher := request.args.get("teacher_id")) is not None:
        got_tasks = select_task_description_where_assignee_and_creator(
            current_user.public_id, teacher
        )
        created_tasks = []
    else:
        got_tasks = select_task_description_where_assignee(
            current_user.public_id
        )
        created_tasks = select_task_description_where_creator(
            current_user.public_id
        )
    return render_template(
        "profile/assignments.html",
        user=current_user,
        got_tasks=got_tasks,
        created_tasks=created_tasks,
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


@profile.route(
    "/profile/games/assign_by_game_id/<uuid:game_id>", methods=["GET", "POST"]
)
def assign_game_by_game_id(game_id: uuid.UUID):
    return redirect(url_for("profile.create_assignment", game_id=game_id))


@profile.route(
    "/profile/games/assign_by_user_id/<uuid:public_id>", methods=["GET", "POST"]
)
def assign_game_by_user_id(public_id: uuid.UUID):
    return redirect(url_for("profile.create_assignment", user_id=public_id))


@profile.route("/profile/games/assign/", methods=["GET", "POST"])
def create_assignment():
    available_games = select_user_games_titles(user_id=current_user.id)
    _, students = get_user_teachers_and_students_public_ids(
        public_id=current_user.public_id
    )
    students_names = [get_username_by_public_id(id_) for id_ in students]
    form = CreateAssignmentForm(students=students_names, games=available_games)
    if (game_id := request.args.get("game_id")) is not None:
        try:
            title = get_title_of_user_game_by_public_id(
                game_id=game_id, user_id=current_user.public_id
            )
            form.game.data = title
        except Exception as e:  # noqa: BLE001
            flash(str(e), "error")
    if (user_id := request.args.get("user_id")) is not None:
        try:
            username = get_username_by_public_id(user_id)
            form.student.data = username
        except Exception as e:  # noqa: BLE001
            flash(str(e), "error")
    if form.validate_on_submit():
        try:
            add_task_to_db(
                game_id=get_game_id_by_title_and_creator(
                    form.game.data, current_user.id
                ),
                assignee_id=get_user_id_by_username(form.student.data),
                created_at=datetime.now(tz=TZ_UTC),
            )
            flash("Task assigned.", "success")
            return redirect(url_for("main.index"))
        except WordGamesError as e:
            if "This game is already assigned to this student." in str(e):
                flash("Such task already exists.", "error")
            else:
                flash("Cannot create this task.", "error")
    return render_template(
        "profile/create_assignment.html",
        stuednts=students,
        games=available_games,
        form=form,
    ), HTTPStatusCode.OK


@profile.route(
    "/profile/assignments/remove/<string:hrid>", methods=["GET", "POST"]
)
def remove_assignment_by_hrid(hrid: str):
    try:
        delete_task_from_db(hrid=hrid, user_public_id=current_user.public_id)
        flash("Task removed.", "success")
        return redirect(url_for("profile.assignments"))
    except WordGamesError as e:
        flash(str(e), "error")


@profile.route("/profile/assignments/remove", methods=["GET", "POST"])
def remove_assignment():
    created_tasks = select_task_natural_identifier_where_creator(
        current_user.public_id
    )
    hrids = [task.hrid for task in created_tasks]
    form = RemoveAssignmentsForm(tasks=hrids)
    if form.validate_on_submit():
        try:
            hrid = form.task.data
            delete_task_from_db(
                hrid=hrid, user_public_id=current_user.public_id
            )
            flash("Task removed.", "success")
        except WordGamesError as e:
            flash(str(e), "error")
        else:
            return redirect(url_for("profile.assignments"))
    return render_template(
        "profile/remove_assignment.html",
        form=form,
    ), HTTPStatusCode.OK


@profile.app_template_filter("format_datetime")
def format_datetime(dt):
    if dt is None:
        return ""
    output = dt.replace(tzinfo=TZ_UTC)
    return output.isoformat()
