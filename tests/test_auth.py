import re
import unittest

from sqlalchemy import func
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import bcrypt, db
from app.users.models import User


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

        self.client = self.app.test_client()

        self.user = User(
            username='existing_user',
            email='existing@example.com',
        )
        self.user.set_password('Existing-pass-123')

        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def csrf_token(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

        match = re.search(
            r'name="csrf_token"[^>]*value="([^"]+)"',
            response.get_data(as_text=True),
        )
        self.assertIsNotNone(match)
        return match.group(1)

    def user_count(self):
        return db.session.scalar(
            db.select(func.count()).select_from(User)
        )

    def registration_data(self, **changes):
        data = {
            'csrf_token': self.csrf_token('/users/register'),
            'username': 'new_user',
            'email': 'New@Example.com',
            'password': 'Register-pass-123',
            'confirm_password': 'Register-pass-123',
        }
        data.update(changes)
        return data

    def login(self, **changes):
        data = {
            'csrf_token': self.csrf_token('/users/login'),
            'username': 'existing_user',
            'password': 'Existing-pass-123',
        }
        data.update(changes)

        return self.client.post('/users/login', data=data)

    def test_register_page(self):
        response = self.client.get('/users/register')
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('name="username"', page)
        self.assertIn('name="email"', page)
        self.assertIn('name="confirm_password"', page)
        self.assertIn('href="/users/register"', page)
        self.assertIn('href="/users/login"', page)
        self.assertNotIn('href="/users/all"', page)

    def test_login_page(self):
        response = self.client.get('/users/login')
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('name="username"', page)
        self.assertIn('name="password"', page)
        self.assertIn('name="remember"', page)
        self.assertIn('name="csrf_token"', page)

    def test_registration_saves_user_with_bcrypt_hash(self):
        response = self.client.post(
            '/users/register',
            data=self.registration_data(),
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers['Location'],
            '/users/login',
        )

        user = db.session.scalar(
            db.select(User).where(
                User.username == 'new_user'
            )
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'new@example.com')
        self.assertNotEqual(user.password, 'Register-pass-123')
        self.assertTrue(
            bcrypt.check_password_hash(
                user.password,
                'Register-pass-123',
            )
        )
        self.assertEqual(self.user_count(), 2)

    def test_registration_rejects_duplicate_identity(self):
        response = self.client.post(
            '/users/register',
            data=self.registration_data(
                username='existing_user',
                email='existing@example.com',
            ),
        )
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'Це ім’я користувача вже зайняте.',
            page,
        )
        self.assertIn(
            'Ця електронна пошта вже зареєстрована.',
            page,
        )
        self.assertEqual(self.user_count(), 1)

    def test_registration_rejects_invalid_data(self):
        response = self.client.post(
            '/users/register',
            data=self.registration_data(
                username='1bad',
                email='not-an-email',
                password='123',
                confirm_password='456',
            ),
        )
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'Введіть коректну електронну пошту.',
            page,
        )
        self.assertIn('Паролі мають збігатися.', page)
        self.assertEqual(self.user_count(), 1)

    def test_login_and_account(self):
        response = self.login(remember='y')

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers['Location'],
            '/users/account',
        )

        with self.client.session_transaction() as session:
            self.assertEqual(
                session['_user_id'],
                str(self.user.id),
            )

        self.assertIsNotNone(
            self.client.get_cookie('remember_token')
        )

        account = self.client.get('/users/account')
        page = account.get_data(as_text=True)

        self.assertEqual(account.status_code, 200)
        self.assertIn('existing_user', page)
        self.assertIn('existing@example.com', page)
        self.assertIn('href="/users/all"', page)
        self.assertNotIn('href="/users/register"', page)
        self.assertNotIn('href="/users/login"', page)

        users_page = self.client.get('/users/all')
        self.assertEqual(users_page.status_code, 200)
        self.assertIn(
            'existing@example.com',
            users_page.get_data(as_text=True),
        )

    def test_login_rejects_wrong_credentials(self):
        cases = [
            ('existing_user', 'wrong-password'),
            ('unknown_user', 'Existing-pass-123'),
        ]

        for username, password in cases:
            with self.subTest(username=username):
                response = self.login(
                    username=username,
                    password=password,
                )

                self.assertEqual(response.status_code, 200)
                self.assertIn(
                    'Невірне ім’я користувача або пароль.',
                    response.get_data(as_text=True),
                )

                with self.client.session_transaction() as session:
                    self.assertNotIn('_user_id', session)

    def test_protected_pages_redirect_guest(self):
        paths = [
            '/users/account',
            '/users/profile',
            '/users/all',
        ]

        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 302)
                self.assertTrue(
                    response.headers['Location'].startswith(
                        '/users/login'
                    )
                )

    def test_authenticated_user_redirects_from_forms(self):
        self.assertEqual(self.login().status_code, 303)

        for path in ['/users/register', '/users/login']:
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response.headers['Location'],
                    '/users/account',
                )

    def test_logout_ends_session_and_remember_cookie(self):
        self.assertEqual(
            self.login(remember='y').status_code,
            303,
        )
        token = self.csrf_token('/users/account')

        response = self.client.post(
            '/users/logout',
            data={'csrf_token': token},
        )

        self.assertEqual(response.status_code, 303)

        with self.client.session_transaction() as session:
            self.assertNotIn('_user_id', session)
            self.assertNotIn('username', session)

        self.assertIsNone(
            self.client.get_cookie('remember_token')
        )
        self.assertEqual(
            self.client.get('/users/account').status_code,
            302,
        )

    def test_logout_requires_csrf(self):
        self.assertEqual(self.login().status_code, 303)

        response = self.client.post('/users/logout')

        self.assertEqual(response.status_code, 400)

        with self.client.session_transaction() as session:
            self.assertEqual(
                session['_user_id'],
                str(self.user.id),
            )

    def test_login_supports_legacy_werkzeug_hash(self):
        legacy_user = User(
            username='legacy_user',
            email='legacy@example.com',
            password=generate_password_hash(
                'Legacy-pass-123',
                method='pbkdf2:sha256',
            ),
        )
        db.session.add(legacy_user)
        db.session.commit()

        response = self.login(
            username='legacy_user',
            password='Legacy-pass-123',
        )

        self.assertEqual(response.status_code, 303)

        with self.client.session_transaction() as session:
            self.assertEqual(
                session['_user_id'],
                str(legacy_user.id),
            )