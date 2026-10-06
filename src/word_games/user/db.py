import uuid
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import (
    CheckConstraint,
    Index,
    PrimaryKeyConstraint,
    String,
    case,
    delete,
    exists,
    literal,
    select,
    union,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from word_games.database import BaseTable
from word_games.db import get_session
from word_games.error import TokenError
from word_games.model import Relation, Role
from word_games.token.controller import deserialize, serialize
from word_games.utils import TZ_UTC


class User(BaseTable, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(64), nullable=False)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[Role] = mapped_column(nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    confirmed: Mapped[bool] = mapped_column(default=False)
    last_seen = Mapped[datetime]

    __table_args__ = (
        Index("idx_user_email", email, unique=True),
        Index("idx_user_username", username, unique=True),
    )

    @property
    def password(self):
        msg = "password is not a readable attribute"
        raise AttributeError(msg)

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        return serialize({"user_id": self.id, "purpose": "confirm_account"})

    def confirm(self, token) -> bool:
        try:
            data = deserialize(token)
        except TokenError:
            return False
        else:
            if (
                data.get("purpose") != "confirm_account"
                and data.get("user_id") != self.id
            ):
                return False
            self.confirmed = True
            with get_session() as session:
                session.add(self)
            return True

    def generate_reset_token(self):
        return serialize({"reset": self.id})

    @staticmethod
    def reset_password(token: str, new_password: str):
        try:
            data = deserialize(token)
        except TokenError:
            return False
        user = User.query.get(data.get("reset"))
        if user is None:
            return False
        user.password = new_password

        with get_session() as session:
            session.add(user)
        return True

    def generate_email_change_token(self, new_email: str):
        return serialize({"change_email": self.id, "new_email": new_email})

    def change_email(self, token: str):
        try:
            data = deserialize(token)
        except TokenError:
            return False
        if data.get("change_email") != self.id:
            return False
        new_email = data.get("new_email")
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        with get_session() as session:
            session.add(self)
        return True

    def ping(self):
        self.last_seen = datetime.now(TZ_UTC)
        with get_session() as session:
            session.add(self)

    def generate_auth_token(self):
        return serialize({"id": self.id})

    @staticmethod
    def verify_auth_token(token: str):
        try:
            data = deserialize(token)
        except TokenError:
            return None
        else:
            return User.query.get(data["id"])

    def __repr__(self):
        return f"<User {self.username}>"


class NetworkEdge(BaseTable):
    """Represent community relation graph nodes. Nodes are not directed.

    The contract is user one and two in rows are ordered in ascending order
    by id field.
    """

    user_one_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    user_two_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    relation: Mapped[Relation] = mapped_column(nullable=False)

    __table_args__ = (
        CheckConstraint("user_one_id < user_two_id", name="ck_ordered_id"),
        PrimaryKeyConstraint(
            "user_one_id", "user_two_id", "relation", name="pk_network_edge"
        ),
        Index("ix_edge_id_one", "user_one_id"),
        Index("ix_edge_id_two", "user_two_id"),
    )


def insert_community_network_edge(edge: NetworkEdge) -> None:
    with get_session() as session:
        session.add(edge)


def delete_community_network_edge(
    user_one_id: UUID,
    user_two_id: UUID,
    relation: Relation,
) -> bool:
    with get_session() as session:
        session.execute(
            delete(NetworkEdge).where(
                (NetworkEdge.user_one_id == user_one_id)
                & (NetworkEdge.user_two_id == user_two_id)
                & (NetworkEdge.relation == relation)
            )
        )


def exists_community_network_edge(
    user_one_id: UUID,
    user_two_id: UUID,
    relation: Relation,
) -> bool:
    with get_session() as session:
        results = session.execute(
            select(
                exists()
                .select_from(NetworkEdge)
                .where(
                    (NetworkEdge.user_one_id == user_one_id)
                    & (NetworkEdge.user_two_id == user_two_id)
                    & (NetworkEdge.relation == relation)
                )
            )
        )
        return results.scalar_one()


def select_user_neighbors_with_their_roles(
    public_id: uuid.UUID,
) -> list[tuple[uuid.UUID, Role | None]]:
    with get_session() as session:
        user_relations = (
            select(
                NetworkEdge.user_one_id,
                NetworkEdge.user_two_id,
                NetworkEdge.relation,
            )
            .where(
                (NetworkEdge.user_one_id == public_id)
                | (NetworkEdge.user_two_id == public_id)
            )
            .subquery()
        )
        results = session.execute(
            union(
                select(
                    user_relations.c.user_two_id,
                    case(
                        (
                            user_relations.c.relation
                            == Relation.student_teacher,
                            literal(Role.teacher),
                        ),
                        else_=literal(Role.student),
                    ),
                ).where(user_relations.c.user_one_id == public_id),
                select(
                    user_relations.c.user_one_id,
                    case(
                        (
                            user_relations.c.relation
                            == Relation.teacher_student,
                            literal(Role.teacher),
                        ),
                        else_=literal(Role.student),
                    ),
                ).where(user_relations.c.user_two_id == public_id),
            )
        )
        return results.all()


def select_neighbours_of_user_where_public_id(public_id: uuid.UUID):
    with get_session() as session:
        results = session.execute(
            select(
                case(
                    (
                        NetworkEdge.user_one_id == public_id,
                        NetworkEdge.user_two_id,
                    ),
                    else_=NetworkEdge.user_one_id,
                )
            ).where(
                (NetworkEdge.user_one_id == public_id)
                | (NetworkEdge.user_two_id == public_id)
            )
        )
        return results.scalars().all()


def select_user_exists_with_public_id(public_id: uuid.UUID) -> bool:
    with get_session() as session:
        results = session.execute(
            select(exists().where(User.public_id == public_id))
        )
    return results.scalar_one()


def select_user_role(public_id: uuid.UUID) -> Role | None:
    with get_session() as session:
        results = session.execute(
            select(User.role).where(User.public_id == public_id)
        )
    return results.scalar_one_or_none()


def select_public_id_by_username(username: str) -> uuid.UUID:
    with get_session() as session:
        results = session.execute(
            select(User.public_id).where(User.username == username)
        )
    return results.scalar_one_or_none()


def select_username_where_public_id(public_id: uuid.UUID) -> str | None:
    with get_session() as session:
        results = session.execute(
            select(User.username).where(User.public_id == public_id)
        )
        return results.scalar_one_or_none()


def select_public_id_where_id(id_: int) -> uuid.UUID | None:
    with get_session() as session:
        results = session.execute(select(User.public_id).where(User.id == id_))
        return results.scalar_one_or_none()
