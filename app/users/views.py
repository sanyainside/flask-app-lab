from flask import flash, redirect, render_template, request, session, url_for

from . import user_bp

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

    return render_template('users/profile.html', title='Профіль', username=username)


@user_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    flash('Ви вийшли із системи.', 'info')
    return redirect(url_for('users.login'))