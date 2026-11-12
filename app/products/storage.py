from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from flask import current_app
from tinydb import TinyDB


INITIAL_PRODUCTS = [
    {
        'id': 1,
        'name': 'Laptop',
        'price': '1200.00',
        'content': 'Ноутбук з Intel Core i7, 16 ГБ RAM і SSD на 512 ГБ.',
        'category': 'Ноутбуки',
        'quantity': 5,
        'image': None,
    },
    {
        'id': 2,
        'name': 'Phone',
        'price': '800.00',
        'content': 'Смартфон з OLED-дисплеєм, подвійною камерою й акумулятором на 5000 мА·год.',
        'category': 'Смартфони',
        'quantity': 8,
        'image': None,
    },
    {
        'id': 3,
        'name': 'PC',
        'price': '1800.00',
        'content': 'Настільний комп’ютер з RTX 4070, 32 ГБ RAM і SSD на 1 ТБ.',
        'category': 'Комп’ютери',
        'quantity': 3,
        'image': None,
    },
]

_storage_lock = Lock()


@contextmanager
def product_table():
    path = Path(current_app.config['PRODUCTS_DB_PATH'])
    path.parent.mkdir(parents=True, exist_ok=True)

    with _storage_lock, TinyDB(path) as database:
        table = database.table('products')
        if 'products' not in database.tables():
            created_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
            table.insert_multiple(
                {**product, 'created_at': created_at}
                for product in INITIAL_PRODUCTS
            )

        yield table