import re

from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, ValidationError


class ProductForm(FlaskForm):
    name = StringField(
        'Назва',
        filters=[lambda value: (value or '').strip()],
        validators=[
            DataRequired(message='Введіть назву.'),
            Length(min=3, message='Назва має містити щонайменше 3 символи.'),
        ],
    )
    content = TextAreaField(
        'Опис',
        validators=[DataRequired(message='Введіть опис.')],
        render_kw={'rows': 5, 'cols': 40},
    )
    price = DecimalField(
        'Ціна',
        places=2,
        validators=[InputRequired(message='Введіть ціну.')],
        render_kw={'step': '0.01', 'min': '0.01'},
    )
    category = SelectField(
        'Категорія',
        choices=[
            ('', 'Оберіть категорію'),
            ('Ноутбуки', 'Ноутбуки'),
            ('Смартфони', 'Смартфони'),
            ('Комп’ютери', 'Комп’ютери'),
            ('Аксесуари', 'Аксесуари'),
        ],
        validators=[DataRequired(message='Оберіть категорію.')],
    )
    quantity = IntegerField(
        'Кількість',
        validators=[
            InputRequired(message='Введіть кількість.'),
            NumberRange(min=0, message='Кількість має бути цілим числом від 0.'),
        ],
    )
    submit = SubmitField('Зберегти товар')

    def validate_price(self, field):
        raw_price = field.raw_data[0].strip()
        if not re.fullmatch(r'[0-9]+(?:\.[0-9]{1,2})?', raw_price):
            raise ValidationError('Введіть ціну з максимум двома знаками після крапки.')
        if field.data is None or field.data <= 0:
            raise ValidationError('Ціна має бути більшою за 0.')