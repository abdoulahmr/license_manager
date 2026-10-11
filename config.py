import os
from dotenv import load_dotenv

load_dotenv()  # safe no-op if no .env file present

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-prod-please')

    # DATABASE_URL is set explicitly in the WSGI file on PythonAnywhere
    # so the path is always absolute inside /home/<user>/.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "licenses.db")}',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'echo': False,
        'pool_pre_ping': True,   # auto-recover dropped conns
    }

    # Use HTTPS when generating external URLs behind PythonAnywhere's proxy
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'https')

    # --- Auth credentials (override in WSGI!) ---
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    API_TOKEN      = os.environ.get('API_TOKEN', 'dev-api-token-change-me')

    # --- Geo-IP enrichment ---
    # Disable on PythonAnywhere free tier — ip-api.com is not on the
    # outbound whitelist there. Set GEOIP_ENABLED=1 on paid tiers.
    GEOIP_ENABLED = os.environ.get('GEOIP_ENABLED', '0') == '1'