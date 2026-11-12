import json
from pathlib import Path

from flask import current_app, flash, redirect, render_template, request, url_for

from . import app

from .forms import ContactForm

@app.route('/')
def resume():
    return render_template('resume.html', title='Резюме')


@app.route('/contact', methods=['GET', 'POST'])
@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    form = ContactForm()

    if form.validate_on_submit():
        entry = {
            'name': form.name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'subject': form.subject.data,
            'message': form.message.data,
        }
        log_path = Path(current_app.instance_path) / 'contact.log'

        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open('a', encoding='utf-8') as log:
                log.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except OSError:
            current_app.logger.exception('Could not write contact submission')
            flash('Не вдалося записати повідомлення. Спробуйте ще раз.', 'danger')
            return render_template('contacts.html', title='Контакти', form=form), 500

        flash('Повідомлення успішно записано.', 'success')
        return redirect(url_for('contacts'), code=303)

    if request.method == 'POST':
        flash('Перевірте поля форми й спробуйте ще раз.', 'danger')
        return render_template('contacts.html', title='Контакти', form=form), 422

    return render_template('contacts.html', title='Контакти', form=form)


@app.route('/homepage')
def home():
    return render_template('homepage.html', title=app.config['SITE_NAME'])