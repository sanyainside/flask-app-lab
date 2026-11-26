from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Regexp,
    ValidationError,
)

from ..extensions import db
from .models import User

from wtforms import BooleanField

class RegistrationForm(FlaskForm):
    username = StringField(
        "Ім’я користувача",
        filters=[lambda value: (value or "").strip()],
        validators=[
            DataRequired(message="Введіть ім’я користувача."),
            Length(
                min=4,
                max=16,
                message="Ім’я має містити від 4 до 16 символів.",
            ),
            Regexp(
                r"^[A-Za-z][A-Za-z0-9_.]*$",
                message=(
                    "Почніть ім’я з латинської літери. "
                    "Дозволені латинські літери, цифри, крапка "
                    "та знак підкреслення."
                ),
            ),
        ],
    )

    email = StringField(
        "Електронна пошта",
        filters=[lambda value: (value or "").strip().lower()],
        validators=[
            DataRequired(message="Введіть електронну пошту."),
            Email(message="Введіть коректну електронну пошту."),
            Length(
                max=120,
                message="Адреса має містити до 120 символів.",
            ),
        ],
    )

    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Введіть пароль."),
            Length(
                min=6,
                max=72,
                message="Пароль має містити від 6 до 72 символів.",
            ),
        ],
    )

    confirm_password = PasswordField(
        "Повторіть пароль",
        validators=[
            DataRequired(message="Повторіть пароль."),
            EqualTo(
                "password",
                message="Паролі мають збігатися.",
            ),
        ],
    )

    submit = SubmitField("Зареєструватися")

    def validate_username(self, field):
        user_id = db.session.scalar(
            db.select(User.id).where(
                User.username == field.data
            )
        )

        if user_id is not None:
            raise ValidationError(
                "Це ім’я користувача вже зайняте."
            )

    def validate_email(self, field):
        user_id = db.session.scalar(
            db.select(User.id).where(
                User.email == field.data
            )
        )

        if user_id is not None:
            raise ValidationError(
                "Ця електронна пошта вже зареєстрована."
            )

    def validate_password(self, field):
        if len((field.data or "").encode("utf-8")) > 72:
            raise ValidationError(
                "Пароль задовгий. Скоротіть його."
            )

class LoginForm(FlaskForm):
    username = StringField(
        "Ім’я користувача",
        filters=[lambda value: (value or "").strip()],
        validators=[
            DataRequired(message="Введіть ім’я користувача."),
            Length(
                max=80,
                message="Ім’я користувача задовге.",
            ),
        ],
    )

    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Введіть пароль."),
            Length(
                max=72,
                message="Пароль задовгий.",
            ),
        ],
    )

    remember = BooleanField("Запам’ятати мене")

    submit = SubmitField("Увійти")


class LogoutForm(FlaskForm):
    submit = SubmitField("Вийти")