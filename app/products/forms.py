import re

from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, ValidationError

from pathlib import Path

from flask_wtf.file import FileAllowed, FileField, FileSize
from PIL import Image


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
    image = FileField(
        'Фото товару',
        validators=[
            FileAllowed(['png', 'jpg', 'jpeg'], 'Допустимі формати: PNG, JPG і JPEG.'),
            FileSize(max_size=2 * 1024 * 1024, message='Фото має бути до 2 МБ.'),
        ],
        render_kw={'accept': '.png,.jpg,.jpeg'},
    )
    submit = SubmitField('Зберегти товар')

    def validate_price(self, field):
        raw_price = field.raw_data[0].strip()
        if not re.fullmatch(r'[0-9]+(?:\.[0-9]{1,2})?', raw_price):
            raise ValidationError('Введіть ціну з максимум двома знаками після крапки.')
        if field.data is None or field.data <= 0:
            raise ValidationError('Ціна має бути більшою за 0.')

    def validate_image(self, field):
        upload = field.data
        if not upload:
            return

        suffix = Path(upload.filename).suffix.lower()
        expected_format = 'PNG' if suffix == '.png' else 'JPEG'

        try:
            with Image.open(upload.stream, formats=[expected_format]) as image:
                image.verify()
        except (OSError, SyntaxError, ValueError, Image.DecompressionBombError) as error:
            raise ValidationError('Файл пошкоджений або має неправильний формат.') from error
        finally:
            upload.stream.seek(0)