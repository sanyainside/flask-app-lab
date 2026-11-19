from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class Post(db.Model):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        Enum(
            'news', 'publication', 'tech', 'other',
            name='post_category',
            create_constraint=True,
            validate_strings=True,
        ),
        default='other',
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=true(),
        nullable=False,
    )
    author: Mapped[str] = mapped_column(
        String(20),
        default='Anonymous',
        server_default='Anonymous',
        nullable=False,
    )

    def __repr__(self):
        return f'<Post id={self.id} title={self.title!r}>'