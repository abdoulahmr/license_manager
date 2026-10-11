import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'agougou-ababas-amigas')

    # SQLite by default; switch to e.g. postgresql+psycopg2://user:pw@host/db for prod
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "licenses.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'echo': False,
        'pool_pre_ping': True,
    }

    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    API_TOKEN      = os.environ.get('API_TOKEN', 'agougou-ababas-amigas')
    GEOIP_ENABLED  = os.environ.get('GEOIP_ENABLED', '1') == '1'