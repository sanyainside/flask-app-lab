import re
import unittest
from datetime import datetime

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.posts.models import Post, Tag
from app.users.models import User


class PostsTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

        password_hash = generate_password_hash(
            'Test-password-123',
            method='pbkdf2:sha256',
        )

        self.user1 = User(
            username='user1',
            email='user1@example.com',
            password=password_hash,
        )
        self.user2 = User(
            username='user2',
            email='user2@example.com',
            password=password_hash,
        )

        self.python_tag = Tag(name='Python')
        self.flask_tag = Tag(name='Flask')
        self.sqlalchemy_tag = Tag(name='SQLAlchemy')

        db.session.add_all([
            self.user1,
            self.user2,
            self.python_tag,
            self.flask_tag,
            self.sqlalchemy_tag,
        ])
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

    def form_data(self, path, **changes):
        data = {
            'csrf_token': self.csrf_token(path),
            'title': 'Тестова публікація',
            'content': 'Текст для перевірки операцій із постами.',
            'enabled': 'y',
            'publish_date': '2026-11-19T10:30',
            'category': 'tech',
            'user_id': str(self.user1.id),
            'tags': [
                str(self.python_tag.id),
                str(self.flask_tag.id),
            ],
        }
        data.update(changes)
        return data

    def saved_post(self, **changes):
        data = {
            'title': 'Початковий заголовок',
            'content': 'Початковий текст.',
            'category': 'news',
            'posted': datetime(2026, 11, 19, 9, 0),
            'is_active': True,
            'user_id': self.user1.id,
        }
        data.update(changes)
        post = Post(**data)
        db.session.add(post)
        db.session.commit()
        return post

    def test_create_post_as_guest(self):
        path = '/post/create'
        response = self.client.post(
            path,
            data=self.form_data(path),
        )

        self.assertEqual(response.status_code, 303)

        post = db.session.scalar(db.select(Post))
        self.assertIsNotNone(post)
        self.assertEqual(post.title, 'Тестова публікація')
        self.assertEqual(post.user_id, self.user1.id)
        self.assertEqual(post.user.username, 'user1')
        self.assertTrue(post.is_active)
        self.assertEqual(
            post.posted,
            datetime(2026, 11, 19, 10, 30),
        )
        self.assertEqual(
            {tag.name for tag in post.tags},
            {'Python', 'Flask'},
        )

        page = self.client.get(response.headers['Location'])
        self.assertEqual(page.status_code, 200)
        self.assertIn(
            'Тестова публікація',
            page.get_data(as_text=True),
        )

    def test_create_post_uses_selected_author(self):
        with self.client.session_transaction() as session:
            session['username'] = 'demo'

        path = '/post/create'
        response = self.client.post(
            path,
            data=self.form_data(
                path,
                user_id=str(self.user2.id),
            ),
        )

        self.assertEqual(response.status_code, 303)

        post = db.session.scalar(db.select(Post))
        self.assertEqual(post.user_id, self.user2.id)
        self.assertEqual(post.user.username, 'user2')

    def test_list_shows_active_posts_in_date_order(self):
        self.saved_post(
            title='Видимий старий',
            posted=datetime(2026, 11, 18, 9, 0),
        )
        self.saved_post(
            title='Видимий новий',
            posted=datetime(2026, 11, 19, 9, 0),
        )
        self.saved_post(
            title='Прихований запис',
            is_active=False,
        )

        response = self.client.get('/post')
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Прихований запис', page)
        self.assertLess(
            page.index('Видимий новий'),
            page.index('Видимий старий'),
        )

    def test_detail_and_missing_post(self):
        post = self.saved_post(
            tags=[self.python_tag, self.flask_tag],
        )

        response = self.client.get(f'/post/{post.id}')
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Початковий текст.', page)
        self.assertIn('user1', page)
        self.assertIn('Python', page)
        self.assertIn('Flask', page)
        self.assertEqual(
            self.client.get('/post/999').status_code,
            404,
        )

    def test_update_changes_author_and_tags_preserves_id(self):
        post = self.saved_post(
            tags=[self.python_tag, self.flask_tag],
        )
        post_id = post.id
        path = f'/post/{post_id}/update'

        form_response = self.client.get(path)
        self.assertEqual(form_response.status_code, 200)

        form_page = form_response.get_data(as_text=True)
        self.assertIn('Початковий заголовок', form_page)
        self.assertIn('2026-11-19T09:00', form_page)

        response = self.client.post(
            path,
            data=self.form_data(
                path,
                title='Оновлений заголовок',
                user_id=str(self.user2.id),
                tags=[str(self.sqlalchemy_tag.id)],
            ),
        )

        self.assertEqual(response.status_code, 303)

        db.session.expire_all()
        updated = db.session.get(Post, post_id)

        self.assertEqual(updated.id, post_id)
        self.assertEqual(
            updated.title,
            'Оновлений заголовок',
        )
        self.assertEqual(updated.user_id, self.user2.id)
        self.assertEqual(updated.user.username, 'user2')
        self.assertEqual(
            updated.posted,
            datetime(2026, 11, 19, 10, 30),
        )
        self.assertEqual(
            {tag.name for tag in updated.tags},
            {'SQLAlchemy'},
        )

    def test_update_can_clear_tags(self):
        post = self.saved_post(tags=[self.python_tag])
        post_id = post.id
        path = f'/post/{post_id}/update'

        response = self.client.post(
            path,
            data=self.form_data(path, tags=[]),
        )

        self.assertEqual(response.status_code, 303)

        db.session.expire_all()
        updated = db.session.get(Post, post_id)
        self.assertEqual(updated.tags, [])

    def test_delete_requires_confirmation_post(self):
        post = self.saved_post(tags=[self.python_tag])
        post_id = post.id
        tag_id = self.python_tag.id
        user_id = self.user1.id
        path = f'/post/{post_id}/delete'

        token = self.csrf_token(path)
        self.assertIsNotNone(
            db.session.get(Post, post_id),
        )

        response = self.client.post(
            path,
            data={'csrf_token': token},
        )

        self.assertEqual(response.status_code, 303)
        self.assertIsNone(db.session.get(Post, post_id))
        self.assertIsNotNone(db.session.get(Tag, tag_id))
        self.assertIsNotNone(db.session.get(User, user_id))
        self.assertEqual(
            self.client.get(f'/post/{post_id}').status_code,
            404,
        )

    def test_invalid_form_does_not_create_post(self):
        path = '/post/create'
        response = self.client.post(
            path,
            data=self.form_data(path, title=''),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'Введіть заголовок.',
            response.get_data(as_text=True),
        )
        self.assertIsNone(
            db.session.scalar(db.select(Post)),
        )

    def test_invalid_author_does_not_create_post(self):
        path = '/post/create'
        response = self.client.post(
            path,
            data=self.form_data(path, user_id='999'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(
            db.session.scalar(db.select(Post)),
        )

    def test_delete_without_csrf_keeps_post(self):
        post = self.saved_post()
        post_id = post.id

        response = self.client.post(
            f'/post/{post_id}/delete',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(
            db.session.get(Post, post_id),
        )