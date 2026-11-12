from flask_wtf import FlaskForm
from wtforms import EmailField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp


class ContactForm(FlaskForm):
    name = StringField('Ім’я', validators=[
        DataRequired(message='Введіть ім’я.'),
        Length(max=80, message='Ім’я має містити до 80 символів.'),
    ])
    email = EmailField('Електронна пошта', validators=[
        DataRequired(message='Введіть електронну пошту.'),
        Email(message='Введіть коректну email-адресу.'),
    ])
    phone = StringField('Телефон (необов’язково)', validators=[
        Optional(),
        Regexp(r'\+?[0-9]{7,15}$', message='Введіть 7–15 цифр, можна з «+» на початку.'),
    ], render_kw={'type': 'tel', 'placeholder': '+380501234567'})
    subject = SelectField('Тема', choices=[
        ('', 'Оберіть тему'),
        ('cooperation', 'Співпраця'),
        ('question', 'Запитання'),
        ('other', 'Інше'),
    ], validators=[DataRequired(message='Оберіть тему повідомлення.')])
    message = TextAreaField('Повідомлення', validators=[
        DataRequired(message='Введіть повідомлення.'),
        Length(max=2000, message='Повідомлення має містити до 2000 символів.'),
    ], render_kw={'rows': 5})
    submit = SubmitField('Надіслати')