from flask import current_app, flash, redirect, render_template
from flask import request, session, url_for
from sqlalchemy.exc import SQLAlchemyError

from . import post_bp
from .forms import DeletePostForm, PostForm
from .models import Post
from ..extensions import db


@post_bp.route('/')
@post_bp.route('')
def all_posts():
    statement = (
        db.select(Post)
        .where(Post.is_active.is_(True))
        .order_by(Post.posted.desc(), Post.id.desc())
    )
    posts = db.session.scalars(statement).all()

    return render_template(
        'posts/all_posts.html',
        title='Пости',
        posts=posts,
    )


@post_bp.route('/<int:post_id>')
def detail_post(post_id):
    post = db.get_or_404(Post, post_id)

    return render_template(
        'posts/detail_post.html',
        title=post.title,
        post=post,
    )


@post_bp.route('/create', methods=['GET', 'POST'])
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            is_active=form.enabled.data,
            posted=form.publish_date.data,
            category=form.category.data,
            author=session.get('username') or 'Anonymous',
        )
        db.session.add(post)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception('Could not create post')
            flash('Не вдалося зберегти пост. Спробуйте ще раз.', 'danger')
            return render_template(
                'posts/add_post.html', title='Додати пост', form=form,
            ), 500

        flash('Пост успішно додано.', 'success')
        return redirect(url_for('posts.detail_post', post_id=post.id), code=303)

    if request.method == 'POST':
        flash('Перевірте поля форми.', 'danger')

    return render_template(
        'posts/add_post.html',
        title='Додати пост',
        form=form,
    )

@post_bp.route('/<int:post_id>/update', methods=['GET', 'POST'])
def update_post(post_id):
    post = db.get_or_404(Post, post_id)
    form = PostForm(obj=post)

    if request.method == 'GET':
        form.enabled.data = post.is_active
        form.publish_date.data = post.posted

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        post.is_active = form.enabled.data
        post.posted = form.publish_date.data

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception('Could not update post')
            flash('Не вдалося зберегти зміни. Спробуйте ще раз.', 'danger')
            return render_template(
                'posts/add_post.html', title='Редагувати пост', form=form,
            ), 500

        flash('Пост успішно оновлено.', 'success')
        return redirect(url_for('posts.detail_post', post_id=post.id), code=303)

    if request.method == 'POST':
        flash('Перевірте поля форми.', 'danger')

    return render_template(
        'posts/add_post.html',
        title='Редагувати пост',
        form=form,
    )

@post_bp.route('/<int:post_id>/delete', methods=['GET', 'POST'])
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    form = DeletePostForm()

    if form.validate_on_submit():
        try:
            db.session.delete(post)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception('Could not delete post')
            flash('Не вдалося видалити пост. Спробуйте ще раз.', 'danger')
            return render_template(
                'posts/delete_confirm.html',
                title='Видалити пост',
                post=post,
                form=form,
            ), 500

        flash('Пост успішно видалено.', 'success')
        return redirect(url_for('posts.all_posts'), code=303)

    if request.method == 'POST':
        flash('Підтвердження недійсне. Відкрийте форму ще раз.', 'danger')
        return render_template(
            'posts/delete_confirm.html',
            title='Видалити пост',
            post=post,
            form=form,
        ), 400

    return render_template(
        'posts/delete_confirm.html',
        title='Видалити пост',
        post=post,
        form=form,
    )