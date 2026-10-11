"""
PythonAnywhere WSGI config for the License Manager.

Replace the path + secrets below, then go to the Web tab and click Reload.
"""

import os
import sys

# ======== Project path ========
PROJECT_HOME = '/home/YOUR_USERNAME/license_manager'
if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

# ======== Secrets (set these!) ========
# Generate each with: python -c "import secrets; print(secrets.token_hex(32))"
os.environ['SECRET_KEY']       = 'CHANGEME-replace-with-64-hex-chars'
os.environ['ADMIN_USERNAME']   = 'admin'
os.environ['ADMIN_PASSWORD']   = 'CHANGEME-strong-password'
os.environ['API_TOKEN']        = 'CHANGEME-64-hex-chars-for-client-sdk'

# ======== Database ========
# Absolute SQLite path inside your home directory.
os.environ['DATABASE_URL'] = f'sqlite:///{PROJECT_HOME}/licenses.db'

# Disable geo-IP enrichment on free tier (ip-api.com not whitelisted).
# Set to '1' on a paid tier if you want it.
os.environ['GEOIP_ENABLED'] = '0'

# Use HTTPS scheme for external URLs.
os.environ['PREFERRED_URL_SCHEME'] = 'https'

# ======== Load the Flask app ========
# PythonAnywhere requires the WSGI callable to be named `application`.
from app import app as application