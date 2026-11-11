from flask import Blueprint

product_bp = Blueprint(
    'products',
    __name__,
    url_prefix='/products',
    template_folder='templates',
)

from . import views