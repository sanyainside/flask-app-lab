from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateTimeLocalField, SelectField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from ..extensions import db
from ..users.models import User

from wtforms import SelectMultipleField
from .models import Tag


class PostForm(FlaskForm):
    title = StringField(
        'Заголовок',
        filters=[lambda value: (value or '').strip()],
        validators=[
            DataRequired(message='Введіть заголовок.'),
            Length(max=150, message='Заголовок має містити до 150 символів.'),
        ],
    )
    content = TextAreaField(
        'Текст поста',
        validators=[DataRequired(message='Введіть текст поста.')],
        render_kw={'rows': 6},
    )
    enabled = BooleanField('Показувати у списку постів', default=True)
    publish_date = DateTimeLocalField(
        'Дата й час публікації (UTC)',
        format='%Y-%m-%dT%H:%M',
        default=datetime.utcnow,
        validators=[DataRequired(message='Вкажіть коректну дату й час.')],
    )
    category = SelectField(
        'Категорія',
        choices=[
            ('news', 'Новини'),
            ('publication', 'Публікації'),
            ('tech', 'Технології'),
            ('other', 'Інше'),
        ],
        default='other',
        validators=[DataRequired(message='Оберіть категорію.')],
    )

    user_id = SelectField(
        "Автор",
        coerce=int,
        validators=[DataRequired(message="Оберіть автора.")],
    )

    tags = SelectMultipleField(
        "Теги",
        coerce=int,
        default=[],
        render_kw={"size": 4},
    )
    
    submit = SubmitField('Зберегти пост')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        users = db.session.scalars(
            db.select(User).order_by(User.id)
        ).all()

        self.user_id.choices = [
            (user.id, user.username)
            for user in users
        ]
        
        tags = db.session.scalars(
            db.select(Tag).order_by(Tag.name)
        ).all()

        self.tags.choices = [
            (tag.id, tag.name)
            for tag in tags
        ]

class DeletePostForm(FlaskForm):
    submit = SubmitField('Так, видалити пост')