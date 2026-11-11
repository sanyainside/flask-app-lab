import unittest

from app import app

class ProductsBlueprintTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_product_list(self):
        response = self.client.get('/products/')
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        for name in ('Laptop', 'Phone', 'PC'):
            self.assertIn(name, page)

    def test_product_detail(self):
        response = self.client.get('/products/1')
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Laptop', page)
        self.assertIn('Intel Core i7', page)
        self.assertIn('1200', page)

    def test_missing_product(self):
        response = self.client.get('/products/999')

        self.assertEqual(response.status_code, 404)