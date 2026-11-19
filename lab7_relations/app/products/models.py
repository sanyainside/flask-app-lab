from typing import List, Optional

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, true

from .. import db


class Category(db.Model):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(128), nullable=False, unique=True,
    )
    products: Mapped[List['Product']] = relationship(
        'Product',
        back_populates='category',
    )

    def __repr__(self):
        return f'<Category id={self.id} name={self.name!r}>'


class Product(db.Model):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('categories.id'),
        nullable=True,
    )
    category: Mapped[Optional['Category']] = relationship(
        'Category',
        back_populates='products',
    )

    def __repr__(self):
        return f'<Product id={self.id} name={self.name!r} price={self.price}>'