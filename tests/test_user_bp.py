import unittest

from app import app

class UsersBlueprintTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_greetings_page(self):
        response = self.client.get('/users/hi/John?age=30')

        self.assertEqual(response.status_code, 200)
        self.assertIn('JOHN', response.get_data(as_text=True))
        self.assertIn('Вік: 30', response.get_data(as_text=True))

    def test_admin_redirect(self):
        response = self.client.get('/users/admin', follow_redirects=True)

        self.assertEqual([item.status_code for item in response.history], [302])
        self.assertEqual(response.status_code, 200)
        self.assertIn('ADMINISTRATOR', response.get_data(as_text=True))
        self.assertIn('Вік: 45', response.get_data(as_text=True))