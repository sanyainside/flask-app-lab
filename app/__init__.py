import os
from pathlib import Path

from flask import Flask, render_template

from .config import CONFIGS
from .extensions import db, migrate


def create_app(config_name=None):
    config_name = config_name or os.environ.get('APP_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    from .views import main_bp
    from .users import user_bp
    from .products import product_bp
    from .posts import post_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(post_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html', title='Сторінку не знайдено'), 404

    return app