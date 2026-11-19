from flask import Blueprint


product_bp = Blueprint('products', __name__)

from . import models