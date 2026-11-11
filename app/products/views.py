from flask import abort, render_template

from . import product_bp


products = [
    {
        'id': 1,
        'name': 'Laptop',
        'price': 1200,
        'content': 'Потужний ноутбук з Intel Core i7, 16 ГБ RAM і SSD на 512 ГБ.',
    },
    {
        'id': 2,
        'name': 'Phone',
        'price': 800,
        'content': 'Смартфон з OLED-дисплеєм 6,5 дюйма, подвійною камерою й акумулятором на 5000 мА·год.',
    },
    {
        'id': 3,
        'name': 'PC',
        'price': 1800,
        'content': 'Настільний комп’ютер з RTX 4070, 32 ГБ RAM і SSD на 1 ТБ.',
    },
]


@product_bp.route('/')
def product_list():
    return render_template('products/products.html', title='Товари', products=products)


@product_bp.route('/<int:product_id>')
def product_detail(product_id):
    product = next((item for item in products if item['id'] == product_id), None)
    if product is None:
        abort(404)

    return render_template(
        'products/detail_product.html',
        title=product['name'],
        product=product,
    )