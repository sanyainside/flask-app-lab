import re
import unittest
from datetime import datetime

from app import create_app
from app.extensions import db
from app.posts.models import Post


class PostsTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

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
            'author': 'Original author',
        }
        data.update(changes)
        post = Post(**data)
        db.session.add(post)
        db.session.commit()
        return post

    def test_create_post_as_guest(self):
        path = '/post/create'
        response = self.client.post(path, data=self.form_data(path))

        self.assertEqual(response.status_code, 303)

        post = db.session.scalar(db.select(Post))
        self.assertIsNotNone(post)
        self.assertEqual(post.title, 'Тестова публікація')
        self.assertEqual(post.author, 'Anonymous')
        self.assertTrue(post.is_active)
        self.assertEqual(post.posted, datetime(2026, 11, 19, 10, 30))

        page = self.client.get(response.headers['Location'])
        self.assertEqual(page.status_code, 200)
        self.assertIn('Тестова публікація', page.get_data(as_text=True))

    def test_create_post_uses_session_author(self):
        with self.client.session_transaction() as session:
            session['username'] = 'demo'

        path = '/post/create'
        response = self.client.post(path, data=self.form_data(path))

        self.assertEqual(response.status_code, 303)
        post = db.session.scalar(db.select(Post))
        self.assertEqual(post.author, 'demo')

    def test_list_shows_active_posts_in_date_order(self):
        self.saved_post(
            title='Видимий старий',
            posted=datetime(2026, 11, 18, 9, 0),
        )
        self.saved_post(
            title='Видимий новий',
            posted=datetime(2026, 11, 19, 9, 0),
        )
        self.saved_post(title='Прихований запис', is_active=False)

        response = self.client.get('/post')
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Прихований запис', page)
        self.assertLess(
            page.index('Видимий новий'),
            page.index('Видимий старий'),
        )

    def test_detail_and_missing_post(self):
        post = self.saved_post()

        response = self.client.get(f'/post/{post.id}')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Початковий текст.', response.get_data(as_text=True))
        self.assertIn('Original author', response.get_data(as_text=True))
        self.assertEqual(self.client.get('/post/999').status_code, 404)

    def test_update_preserves_author_and_id(self):
        post = self.saved_post()
        post_id = post.id
        path = f'/post/{post_id}/update'

        form_page = self.client.get(path).get_data(as_text=True)
        self.assertIn('Початковий заголовок', form_page)
        self.assertIn('2026-11-19T09:00', form_page)

        response = self.client.post(
            path,
            data=self.form_data(path, title='Оновлений заголовок'),
        )

        self.assertEqual(response.status_code, 303)
        updated = db.session.get(Post, post_id)
        self.assertEqual(updated.title, 'Оновлений заголовок')
        self.assertEqual(updated.author, 'Original author')
        self.assertEqual(updated.id, post_id)
        self.assertEqual(updated.posted, datetime(2026, 11, 19, 10, 30))

    def test_delete_requires_confirmation_post(self):
        post = self.saved_post()
        post_id = post.id
        path = f'/post/{post_id}/delete'

        token = self.csrf_token(path)
        self.assertIsNotNone(db.session.get(Post, post_id))

        response = self.client.post(path, data={'csrf_token': token})

        self.assertEqual(response.status_code, 303)
        self.assertIsNone(db.session.get(Post, post_id))
        self.assertEqual(
            self.client.get(f'/post/{post_id}').status_code, 404,
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
        self.assertIsNone(db.session.scalar(db.select(Post)))

    def test_delete_without_csrf_keeps_post(self):
        post = self.saved_post()
        post_id = post.id

        response = self.client.post(f'/post/{post_id}/delete')

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(db.session.get(Post, post_id))