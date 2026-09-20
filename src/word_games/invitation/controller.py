import uuid
from datetime import datetime

from word_games.config.glob import GLOBAL_SETTINGS
from word_games.db import get_session
from word_games.error import PendingInvitationError, WordGamesError
from word_games.invitation.db import (
    Invitation,
    select_invitation_exists,
    select_invitation_status,
    select_pending_invitation_exists,
    select_user_received_invitatitions,
    select_user_sent_invitatitions,
    select_user_sent_pending_invitatitions,
    update_status,
)
from word_games.invitation.model import Status
from word_games.user.controller import raise_if_user_not_exists
from word_games.utils import TZ_UTC


def send_invitation(sender: uuid.UUID, receiver: uuid.UUID):
    try:
        raise_if_reached_pending_invitations_limit(sender)
        _raise_if_invitation_is_pending(sender, receiver)
        new_inv = Invitation(
            sender_id=sender,
            receiver_id=receiver,
            send_date=datetime.now(tz=TZ_UTC),
            status=Status.PENDING,
        )
        with get_session() as session:
            session.add(new_inv)
    except Exception as e:
        msg = f"Cannot send an invitation from {sender} to {receiver}"
        raise WordGamesError(msg) from e


def accept_invitation(invitation_id: uuid.UUID) -> None:
    try:
        _raise_if_invitation_not_exists(invitation_id)
        _raise_if_status_is_not_pending(invitation_id)
        update_status(invitation_id, Status.ACCEPTED)
    except Exception as e:
        msg = "Cannot accept this invitation."
        raise WordGamesError(msg) from e


def reject_invitation(invitation_id: uuid.UUID) -> None:
    try:
        _raise_if_invitation_not_exists(invitation_id)
        _raise_if_status_is_not_pending(invitation_id)
        update_status(invitation_id, Status.REJECTED)
    except Exception as e:
        msg = "Cannot reject this invitation."
        raise WordGamesError(msg) from e


def cancel_invitation(invitation_id: uuid.UUID) -> None:
    try:
        _raise_if_invitation_not_exists(invitation_id)
        _raise_if_status_is_not_pending(invitation_id)
        update_status(invitation_id, Status.CANCELLED)
    except Exception as e:
        msg = "Cannot cancel this invitation."
        raise WordGamesError(msg) from e


def get_all_user_received_invitations(public_id: uuid.UUID) -> None:
    try:
        raise_if_user_not_exists(public_id)
        select_user_received_invitatitions(public_id)
    except Exception as e:
        msg = "Cannot cancel this invitation."
        raise WordGamesError(msg) from e


def get_all_user_sent_invitations(public_id: uuid.UUID) -> None:
    try:
        raise_if_user_not_exists(public_id)
        select_user_sent_invitatitions(public_id)
    except Exception as e:
        msg = "Cannot cancel this invitation."
        raise WordGamesError(msg) from e


def _raise_if_invitation_is_pending(
    sender_id: uuid.UUID, receiver_id: uuid.UUID
):
    if select_pending_invitation_exists(
        sender_id=sender_id,
        receiver_id=receiver_id,
    ):
        msg = "Such invitations already pending."
        raise PendingInvitationError(msg)


def _raise_if_invitation_not_exists(invitation_id: uuid.UUID) -> None:
    if not select_invitation_exists(invitation_id):
        msg = "Such invitations not exists."
        raise WordGamesError(msg)


def _raise_if_status_is_not_pending(invitation_id: uuid.UUID) -> None:
    if select_invitation_status(invitation_id) != Status.PENDING:
        msg = "Invitation status is not pending."
        raise WordGamesError(msg)


def raise_if_reached_pending_invitations_limit(sender_id: uuid.UUID) -> None:
    if (
        len(select_user_sent_pending_invitatitions(sender_id))
        >= GLOBAL_SETTINGS.pending_invitations_limit
    ):
        msg = "Reached sent invitations limit."
        raise WordGamesError(msg)
