from flask import redirect, render_template, request, url_for

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