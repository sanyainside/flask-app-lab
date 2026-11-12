from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from flask import current_app, url_for

from . import product_bp


def remove_product_image(filename):
    if filename:
        try:
            (Path(product_bp.static_folder) / filename).unlink(missing_ok=True)
        except OSError:
            current_app.logger.exception('Could not remove product image')


@contextmanager
def store_product_image(upload):
    if not upload:
        yield None
        return

    suffix = Path(upload.filename).suffix.lower()
    filename = f'uploads/{uuid4().hex}{suffix}'
    path = Path(product_bp.static_folder) / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        upload.save(path)
        yield filename
    except Exception:
        remove_product_image(filename)
        raise


@product_bp.app_template_global()
def product_image_url(filename):
    if filename and (Path(product_bp.static_folder) / filename).is_file():
        return url_for('products.static', filename=filename)
    return None