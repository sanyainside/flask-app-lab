from flask import Blueprint

product_bp = Blueprint(
    'products',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/product-static',
)

from . import views