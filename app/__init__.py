from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('../config.py')

from . import views

from .users import user_bp

app.register_blueprint(user_bp)

from .products import product_bp

app.register_blueprint(product_bp)