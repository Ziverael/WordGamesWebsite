import uuid
from datetime import datetime

from sqlalchemy import (
    UUID,
    DateTime,
    Index,
    exists,
    select,
    update,
)
from sqlalchemy.orm import Mapped, mapped_column

from word_games.database import BaseTable
from word_games.db import get_session
from word_games.invitation.model import Status


class Invitation(BaseTable):
    """Represent invitation from teacher to a student."""

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    receiver_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    status: Mapped[Status]
    send_date: Mapped[datetime]
    status_update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    __table_args__ = (
        Index("idx_invitation_public_id", public_id, unique=True),
    )


def update_status(invitation_id: uuid.UUID, status: Status) -> None:
    with get_session() as session:
        session.execute(
            update(Invitation)
            .where(Invitation.public_id == invitation_id)
            .values(status=status)
        )


def select_pending_invitation_exists(
    sender_id: uuid.UUID, receiver_id: uuid.UUID
) -> bool:
    with get_session() as session:
        results = session.execute(
            select(
                exists().where(
                    (Invitation.sender_id == sender_id)
                    & (Invitation.receiver_id == receiver_id)
                    & (Invitation.status == Status.PENDING)
                )
            )
        )
        return results.scalar_one()


def select_user_received_invitatitions(
    public_id: uuid.UUID,
) -> list[Invitation]:
    with get_session() as session:
        results = session.execute(
            select(Invitation).where(Invitation.receiver_id == public_id)
        )
        return results.mappings().all()


def select_user_sent_invitatitions(public_id: uuid.UUID) -> list[Invitation]:
    with get_session() as session:
        results = session.execute(
            select(Invitation).where(Invitation.sender_id == public_id)
        )
        return results.mappings().all()


def select_user_sent_pending_invitatitions(
    public_id: uuid.UUID,
) -> list[Invitation]:
    with get_session() as session:
        results = session.execute(
            select(Invitation).where(
                (Invitation.sender_id == public_id)
                & (Invitation.status == Status.PENDING)
            )
        )
        return results.mappings().all()


def select_invitation_exists(invitation_id: uuid.UUID) -> bool:
    with get_session() as session:
        results = session.execute(
            select(
                exists(Invitation).where(Invitation.public_id == invitation_id)
            )
        )
        return results.scalar_one()


def select_invitation_status(invitation_id: uuid.UUID) -> Status | None:
    with get_session() as session:
        results = session.execute(
            select(Invitation.status).where(
                Invitation.public_id == invitation_id
            )
        )
        return results.scalar_one()
