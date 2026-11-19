import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / '.env')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SITE_NAME = 'Навчальний сайт на Flask'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///data.sqlite',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRODUCTS_DB_PATH = PROJECT_ROOT / 'data' / 'products.json'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-only-secret'


class ProductionConfig(Config):
    DEBUG = False


CONFIGS = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}