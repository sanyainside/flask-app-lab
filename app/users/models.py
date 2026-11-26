from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from typing import List

from ..extensions import db, bcrypt, login_manager
from werkzeug.security import check_password_hash as check_werkzeug_hash

from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    posts: Mapped[List["Post"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

    def check_password(self, password):
        try:
            if self.password.startswith(("pbkdf2:", "scrypt:")):
                return check_werkzeug_hash(self.password, password)

            return bcrypt.check_password_hash(
                self.password,
                password,
            )
        except (ValueError, TypeError):
            return False

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"

@login_manager.user_loader
def load_user(user_id):
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None

    return db.session.get(User, user_id)