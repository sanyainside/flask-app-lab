from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateTimeLocalField, SelectField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


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
    submit = SubmitField('Зберегти пост')

class DeletePostForm(FlaskForm):
    submit = SubmitField('Так, видалити пост')