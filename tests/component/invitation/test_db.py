import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from word_games.invitation import db


class TestInvitation:
    def test_insert(self, db_session, invitation_factory):
        # given
        inv = invitation_factory.build()

        # when
        db_session.add(inv)
        db_session.commit()

        # then
        stmt = select(db.Invitation)
        invs_in_db = db_session.scalars(stmt).all()
        assert len(invs_in_db) == 1
        assert invs_in_db[0] == inv

    def test_init_update_status_date(self, db_session, invitation_factory):
        # given
        inv = invitation_factory.build(status_update_date=None)

        # when
        db_session.add(inv)
        db_session.commit()

        # then
        stmt = select(db.Invitation)
        inv_in_db = db_session.scalars(stmt).one()
        assert inv_in_db.status_update_date is None

    def test_trigger_update_status_date(self, db_session, invitation_factory):
        # given
        public_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
        inv = invitation_factory.build(
            status_update_date=None, public_id=public_id
        )
        db_session.add(inv)
        db_session.commit()
        current_time = datetime.now(tz=UTC)

        # when
        db_session.execute(
            update(db.Invitation)
            .where(db.Invitation.public_id == public_id)
            .values(status=db.Status.ACCEPTED)
        )

        # then
        stmt = select(db.Invitation).where(db.Invitation.public_id == public_id)
        inv_in_db = db_session.scalars(stmt).one()
        assert abs(inv_in_db.status_update_date - current_time) <= timedelta(
            minutes=1
        )

    def test_unique_public_id_raises(self, db_session, user_factory):
        # given
        public_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
        inv1 = user_factory.build(public_id=public_id)
        inv2 = user_factory.build(public_id=public_id)

        # when
        db_session.add(inv1)
        db_session.commit()
        db_session.add(inv2)

        # then
        with pytest.raises(
            IntegrityError,
            match=r"duplicate key value violates unique constraint \"unique_public_id\"",
        ):
            db_session.commit()


@pytest.mark.parametrize("status", list(db.Status))
def test_update_status(db_session, invitation_factory, status: db.Status):
    # given
    public_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
    inv = invitation_factory.build(status_update_date=None, public_id=public_id)
    db_session.add(inv)
    db_session.commit()

    # when
    db.update_status(public_id, status)

    # then
    stmt = select(db.Invitation.status).where(
        db.Invitation.public_id == public_id
    )
    status_in_db = db_session.execute(stmt).scalar_one()
    assert status_in_db == status


def test_update_status__invitation_not_exists(db_session):
    # given
    status = db.Status.ACCEPTED
    public_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

    # when
    db.update_status(public_id, status)

    # then
    stmt = select(db.Invitation.status).where(
        db.Invitation.public_id == public_id
    )
    status_in_db = db_session.execute(stmt).scalar_one_or_none()
    assert status_in_db is None


@pytest.mark.parametrize(
    ("invitations_in_db", "expected"),
    [
        pytest.param((), False, id="missing"),
        pytest.param(
            (
                db.Invitation(
                    id=1,
                    public_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    sender_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    receiver_id=uuid.UUID(
                        "00000000-0000-0000-0000-000000000001"
                    ),
                    status=db.Status.PENDING,
                    send_date=datetime(2000, 1, 1),
                ),
            ),
            True,
            id="exists",
        ),
        pytest.param(
            (
                db.Invitation(
                    id=1,
                    public_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    sender_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    receiver_id=uuid.UUID(
                        "00000000-0000-0000-0000-000000000001"
                    ),
                    status=db.Status.ACCEPTED,
                    send_date=datetime(2000, 1, 1),
                ),
            ),
            False,
            id="exists-accepted",
        ),
        pytest.param(
            (
                db.Invitation(
                    id=1,
                    public_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    sender_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    receiver_id=uuid.UUID(
                        "00000000-0000-0000-0000-000000000001"
                    ),
                    status=db.Status.REJECTED,
                    send_date=datetime(2000, 1, 1),
                ),
            ),
            False,
            id="exists-rejected",
        ),
        pytest.param(
            (
                db.Invitation(
                    id=1,
                    public_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    sender_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    receiver_id=uuid.UUID(
                        "00000000-0000-0000-0000-000000000001"
                    ),
                    status=db.Status.CANCELLED,
                    send_date=datetime(2000, 1, 1),
                ),
            ),
            False,
            id="exists-canceled",
        ),
        pytest.param(
            (
                db.Invitation(
                    id=1,
                    public_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    sender_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
                    receiver_id=uuid.UUID(
                        "00000000-0000-0000-0000-000000000001"
                    ),
                    status=db.Status.PENDING,
                    send_date=datetime(2000, 1, 1),
                ),
            ),
            False,
            id="wrong-sender",
        ),
        pytest.param(
            (
                db.Invitation(
                    id=1,
                    public_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    sender_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                    receiver_id=uuid.UUID(
                        "00000000-0000-0000-0000-000000000002"
                    ),
                    status=db.Status.PENDING,
                    send_date=datetime(2000, 1, 1),
                ),
            ),
            False,
            id="wrong-receiver",
        ),
    ],
)
def test_select_pending_invitation_exists(
    db_session,
    invitation_factory,
    invitations_in_db: list[db.Invitation],
    expected: bool,
):
    # given
    sender_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
    receiver_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    for inv in invitations_in_db:
        db_session.add(inv)
    db_session.commit()

    # when
    results = db.select_pending_invitation_exists(sender_id, receiver_id)

    # then
    assert results == expected
