from flask import abort, render_template
from tinydb import Query

from . import product_bp
from .storage import product_table


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