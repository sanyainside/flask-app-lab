import re

from flask import flash, redirect, render_template, request, session, url_for, abort
from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..extensions import db
from .forms import LoginForm, LogoutForm, RegistrationForm
from .models import User

from . import user_bp

COOKIE_PREFIX = 'lab4_cookie_'

THEME_COOKIE = 'lab4_profile_theme'

@user_bp.app_context_processor
def inject_logout_form():
    return {"logout_form": LogoutForm()}

@user_bp.route('/hi/<string:name>')
def greetings(name):
    age = request.args.get('age', type=int)

    return render_template(
        'users/hi.html',
        title='Привітання',
        name=name.upper(),
        age=age,
    )


@user_bp.route('/admin')
def admin():
    return redirect(url_for('users.greetings', name='administrator', age=45))

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash(
                'Ім’я користувача або електронна пошта вже зайняті.',
                'danger',
            )
            return render_template(
                'users/register.html',
                title='Реєстрація',
                form=form,
            ), 409
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception('Could not register user')
            flash(
                'Не вдалося створити обліковий запис. Спробуйте ще раз.',
                'danger',
            )
            return render_template(
                'users/register.html',
                title='Реєстрація',
                form=form,
            ), 500

        flash(
            'Реєстрація успішна. Тепер увійдіть у свій обліковий запис.',
            'success',
        )
        return redirect(url_for('users.login'), code=303)

    return render_template(
        'users/register.html',
        title='Реєстрація',
        form=form,
    )

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            db.select(User).where(
                User.username == form.username.data
            )
        )

        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            session['username'] = user.username

            flash('Ви успішно увійшли.', 'success')
            return redirect(url_for('users.account'), code=303)

        flash('Невірне ім’я користувача або пароль.', 'danger')

    return render_template(
        'users/login.html',
        title='Вхід',
        form=form,
    )

@user_bp.route('/account')
@login_required
def account():
    return render_template(
        'users/account.html',
        title='Обліковий запис',
    )

@user_bp.route('/profile')
@login_required
def profile():
    cookies = {
        name[len(COOKIE_PREFIX):]: value
        for name, value in request.cookies.items()
        if name.startswith(COOKIE_PREFIX)
    }

    theme = 'dark' if request.cookies.get(THEME_COOKIE) == 'dark' else 'light'

    return render_template(
        'users/profile.html',
        title='Профіль',
        username=current_user.username,
        cookies=cookies,
        theme=theme
    )


@user_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    form = LogoutForm()

    if not form.validate_on_submit():
        abort(400, description='Недійсне підтвердження виходу.')

    logout_user()
    session.pop('username', None)

    flash('Ви вийшли із системи.', 'info')
    return redirect(url_for('users.login'), code=303)

@user_bp.route('/profile/cookies', methods=['POST'])
@login_required
def manage_cookies():

    action = request.form.get('action')
    response = redirect(url_for('users.profile'))

    if action == 'delete_all':
        for name in request.cookies:
            if name.startswith(COOKIE_PREFIX):
                response.delete_cookie(name)

        flash('Усі записи з таблиці кукі видалено.', 'success')
        return response

    key = request.form.get('key', '').strip()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,32}', key):
        flash('Ключ має містити від 1 до 32 латинських літер, цифр, дефісів або підкреслень.', 'danger')
        return response

    name = COOKIE_PREFIX + key

    if action == 'add':
        value = request.form.get('value', '')
        max_age = request.form.get('max_age', type=int)

        if not value.strip() or len(value) > 100 or max_age is None or not 1 <= max_age <= 2592000:
            flash('Введіть значення до 100 символів і термін дії від 1 секунди до 30 днів.', 'danger')
            return response

        response.set_cookie(name, value, max_age=max_age, httponly=True, samesite='Lax')
        flash(f'Кукі «{key}» збережено.', 'success')

    elif action == 'delete':
        if name in request.cookies:
            response.delete_cookie(name)
            flash(f'Кукі «{key}» видалено.', 'success')
        else:
            flash(f'Кукі «{key}» не знайдено.', 'warning')

    else:
        flash('Невідома дія.', 'danger')

    return response

@user_bp.route('/profile/theme', methods=['POST'])
@login_required
def set_theme():

    theme = request.form.get('theme')
    response = redirect(url_for('users.profile'))

    if theme not in ('light', 'dark'):
        flash('Оберіть світлу або темну тему.', 'danger')
        return response

    response.set_cookie(
        THEME_COOKIE, theme, max_age=30 * 24 * 60 * 60,
        httponly=True, samesite='Lax',
    )
    return response

@user_bp.route('/all')
@login_required
def user_list():
    users = db.session.scalars(
        db.select(User).order_by(User.id)
    ).all()

    return render_template(
        'users/user_list.html',
        title='Зареєстровані користувачі',
        users=users,
        total_users=len(users),
    )