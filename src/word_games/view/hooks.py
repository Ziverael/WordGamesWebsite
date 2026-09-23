from __future__ import annotations

from typing import TYPE_CHECKING

from flask import flash, redirect, url_for
from flask_login import current_user

from word_games.model import Role


if TYPE_CHECKING:
    from flask import Response


def admit_teacher(msg: str, redirect_target: Response | None = None):
    if current_user.role != Role.teacher:
        flash(msg, "error")
        return redirect_target or redirect(url_for("main.index"))
    return None


def admit_student(msg: str, redirect_target: Response | None = None):
    if current_user.role != Role.student:
        flash(msg, "error")
        return redirect_target or redirect(url_for("main.index"))
    return None
