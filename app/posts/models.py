from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, Text, true, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

from typing import List, Optional

post_tags = db.Table(
    "post_tags",
    db.Column(
        "post_id",
        db.Integer,
        db.ForeignKey("post.id", name="fk_post_tags_post_id_post"),
        primary_key=True,
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id", name="fk_post_tags_tag_id_tags"),
        primary_key=True,
    ),
)


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

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            name="fk_post_user_id_users",
        ),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="posts",
    )

    user: Mapped[Optional["User"]] = relationship(
        back_populates="posts",
    )

    tags: Mapped[List["Tag"]] = relationship(
        secondary=post_tags,
        back_populates="posts",
    )

    def __repr__(self):
        return f'<Post id={self.id} title={self.title!r}>'

class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    posts: Mapped[List["Post"]] = relationship(
        secondary=post_tags,
        back_populates="tags",
    )

    def __repr__(self):
        return f"<Tag id={self.id} name={self.name!r}>"