from . import main
from flask import jsonify, render_template
from flask_login import current_user, login_required

from word_games.constants import HTTPStatusCode
from word_games.invitation.controller import get_user_pending_invitaitons_count


@main.route("/", methods=["GET", "POST"])
def index():
    return render_template(
        "index.html",
    ), HTTPStatusCode.OK


@main.get("/api/notifications/unread-count")
@login_required
def unread_notification_count():
    count = get_user_pending_invitaitons_count(current_user.public_id)
    return jsonify({"invitations": count or 0})
