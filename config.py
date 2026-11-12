import os
from pathlib import Path

SITE_NAME = 'Навчальний сайт на Flask'
SECRET_KEY = os.environ.get('SECRET_KEY')
PRODUCTS_DB_PATH = Path(__file__).resolve().parent / 'data' / 'products.json'