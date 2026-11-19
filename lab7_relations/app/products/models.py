from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .. import db


class Product(db.Model):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self):
        return f'<Product id={self.id} name={self.name!r} price={self.price}>'