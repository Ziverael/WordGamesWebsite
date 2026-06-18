from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import JSON, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from word_games.database import BaseTable
from word_games.db import get_session
from word_games.error import TokenError
from word_games.model import Role
from word_games.utils import TZ_UTC, deserialize, serialize


class Game(BaseTable):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    created_at: Mapped[datetime]
    creator: Mapped[int]
    content: Mapped[dict] = mapped_column(JSON)


class Task(BaseTable):
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int]
    assignee_id: Mapped[int]
    created_at: Mapped[datetime]
    viewed_at: Mapped[datetime | None]
    recently_viewed_at: Mapped[datetime | None]


class User(BaseTable, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(64))
    username: Mapped[str] = mapped_column(String(64))
    role: Mapped[Role]
    password_hash: Mapped[str] = mapped_column(String(128))
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
        return serialize({"confirm": self.id})

    def confirm(self, token) -> bool:
        try:
            data = deserialize(token)
        except TokenError:
            return False
        else:
            if data.get("confirm") != self.id:
                return False
            self.confirmed = True
            session = get_session()
            session.add(self)
            return True

    def generate_reset_token(self):
        return serialize({"reset": self.id})

    @staticmethod
    def reset_password(token: bytes, new_password: str):
        try:
            data = deserialize(token)
        except TokenError:
            return False
        user = User.query.get(data.get("reset"))
        if user is None:
            return False
        user.password = new_password

        session = get_session()
        session.add(user)
        return True

    def generate_email_change_token(self, new_email: str):
        return serialize({"change_email": self.id, "new_email": new_email})

    def change_email(self, token: bytes):
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
        session = get_session()
        session.add(self)
        return True

    def ping(self):
        self.last_seen = datetime.now(TZ_UTC)
        session = get_session()
        session.add(self)

    def generate_auth_token(self):
        return serialize({"id": self.id})

    @staticmethod
    def verify_auth_token(token: bytes):
        try:
            data = deserialize(token)
        except TokenError:
            return None
        else:
            return User.query.get(data["id"])

    def __repr__(self):
        return f"<User {self.username}>"
