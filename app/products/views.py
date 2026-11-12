from datetime import datetime, timezone
from decimal import Decimal

from flask import abort, flash, redirect, render_template, request, url_for

from .forms import ProductForm
from tinydb import Query

from . import product_bp
from .storage import product_table

from .images import remove_product_image, store_product_image

@product_bp.route('/products/')
@product_bp.route('/product')
def product_list():
    with product_table() as table:
        products = table.all()

    return render_template('products/products.html', title='Товари', products=products)


@product_bp.route('/products/<int:product_id>')
@product_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    with product_table() as table:
        product = table.get(Query().id == product_id)

    if product is None:
        abort(404)

    return render_template(
        'products/detail_product.html',
        title=product['name'],
        product=product,
    )

def product_fields(form):
    return {
        'name': form.name.data,
        'content': form.content.data.strip(),
        'price': format(form.price.data, '.2f'),
        'category': form.category.data,
        'quantity': form.quantity.data,
    }


@product_bp.route('/product/add', methods=['GET', 'POST'])
def product_add():
    form = ProductForm()

    if form.validate_on_submit():
        product = product_fields(form)
        with store_product_image(form.image.data) as image, product_table() as table:
            product_id = max((item['id'] for item in table.all()), default=0) + 1
            product['id'] = product_id
            product['created_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
            product['image'] = image
            table.insert(product)

        flash('Товар успішно додано.', 'success')
        return redirect(url_for('products.product_detail', product_id=product_id), code=303)

    if request.method == 'POST':
        flash('Перевірте поля форми.', 'danger')

    return render_template(
        'products/product_form.html', title='Додати товар', form=form,
    )

@product_bp.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
def product_edit(product_id):
    query = Query().id == product_id

    with product_table() as table:
        product = table.get(query)

    if product is None:
        abort(404)

    initial_data = {**product, 'price': Decimal(product['price']), 'image': None}
    form = ProductForm(data=initial_data)

    if form.validate_on_submit():
        with store_product_image(form.image.data) as image, product_table() as table:
            current_product = table.get(query)
            if current_product is None:
                abort(404)

            changes = product_fields(form)
            if image:
                changes['image'] = image

            table.update(changes, query)

            if image:
                remove_product_image(current_product.get('image'))

        flash('Зміни збережено.', 'success')
        return redirect(url_for('products.product_detail', product_id=product_id), code=303)

    if request.method == 'POST':
        flash('Перевірте поля форми.', 'danger')

    return render_template(
        'products/product_form.html', title='Редагувати товар', form=form,
    )