import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tinydb import Query

from app import app
from app.products.storage import product_table


class ProductsBlueprintTests(unittest.TestCase):
    def setUp(self):
        temp_dir = TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)

        config = patch.dict(app.config, {
            'TESTING': True,
            'SECRET_KEY': 'test-only-secret',
            'PRODUCTS_DB_PATH': Path(temp_dir.name) / 'products.json',
        })
        config.start()
        self.addCleanup(config.stop)
        self.client = app.test_client()

    def csrf_token(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        match = re.search(
            r'name="csrf_token"[^>]*value="([^"]+)"',
            response.get_data(as_text=True),
        )
        self.assertIsNotNone(match)
        return match.group(1)

    def product_data(self, form_path):
        return {
            'csrf_token': self.csrf_token(form_path),
            'name': 'Тестовий монітор',
            'content': 'Монітор для перевірки CRUD.',
            'price': '249.90',
            'category': 'Аксесуари',
            'quantity': '0',
        }

    def stored_product(self, product_id):
        with app.app_context(), product_table() as table:
            return table.get(Query().id == product_id)

    def test_product_list(self):
        response = self.client.get('/product')
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)

        for name in ('Laptop', 'Phone', 'PC'):
            self.assertIn(name, page)

    def test_product_detail_and_missing_product(self):
        response = self.client.get('/product/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Intel Core i7', response.get_data(as_text=True))
        self.assertEqual(self.client.get('/product/999').status_code, 404)

    def test_create_product(self):
        path = '/product/add'
        response = self.client.post(path, data=self.product_data(path))

        self.assertEqual(response.status_code, 303)
        detail = self.client.get(response.headers['Location'])
        self.assertEqual(detail.status_code, 200)
        self.assertIn('Тестовий монітор', detail.get_data(as_text=True))

        product_id = int(response.headers['Location'].rsplit('/', 1)[1])
        product = self.stored_product(product_id)
        self.assertEqual(product['price'], '249.90')
        self.assertEqual(product['quantity'], 0)
        self.assertTrue(product['created_at'])

    def test_edit_preserves_id_and_creation_date(self):
        original = self.stored_product(1)
        path = '/product/1/edit'

        response = self.client.post(path, data=self.product_data(path))

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], '/product/1')
        updated = self.stored_product(1)
        self.assertEqual(updated['name'], 'Тестовий монітор')
        self.assertEqual(updated['id'], original['id'])
        self.assertEqual(updated['created_at'], original['created_at'])

    def test_delete_product(self):
        token = self.csrf_token('/product/1/confirm-delete')
        response = self.client.post(
            '/product/1/delete', data={'csrf_token': token},
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], '/product')
        self.assertEqual(self.client.get('/product/1').status_code, 404)

    def test_delete_requires_post_and_csrf(self):
        path = '/product/1/delete'

        self.assertEqual(self.client.get(path).status_code, 405)
        self.assertEqual(self.client.post(path).status_code, 400)
        self.assertEqual(self.client.get('/product/1').status_code, 200)