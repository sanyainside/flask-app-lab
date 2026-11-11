import re

from flask import flash, redirect, render_template, request, session, url_for

from . import user_bp

COOKIE_PREFIX = 'lab4_cookie_'

THEME_COOKIE = 'lab4_profile_theme'

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

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('users/login.html', title='Вхід')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if username == 'demo' and password == 'flask-demo-123':
        session['username'] = username
        flash('Ви успішно увійшли.', 'success')
        return redirect(url_for('users.profile'))

    flash('Невірний логін або пароль.', 'danger')
    return redirect(url_for('users.login'))


@user_bp.route('/profile')
def profile():
    username = session.get('username')
    if username is None:
        flash('Спочатку увійдіть у систему.', 'danger')
        return redirect(url_for('users.login'))

    cookies = {
        name[len(COOKIE_PREFIX):]: value
        for name, value in request.cookies.items()
        if name.startswith(COOKIE_PREFIX)
    }

    theme = 'dark' if request.cookies.get(THEME_COOKIE) == 'dark' else 'light'

    return render_template(
        'users/profile.html',
        title='Профіль',
        username=username,
        cookies=cookies,
        theme=theme
    )


@user_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    flash('Ви вийшли із системи.', 'info')
    return redirect(url_for('users.login'))

@user_bp.route('/profile/cookies', methods=['POST'])
def manage_cookies():
    if 'username' not in session:
        flash('Спочатку увійдіть у систему.', 'danger')
        return redirect(url_for('users.login'))

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
def set_theme():
    if 'username' not in session:
        flash('Спочатку увійдіть у систему.', 'danger')
        return redirect(url_for('users.login'))

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