import os
import click
from flask import Flask, request, session, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from extensions import db
from models import Product, License, Activation


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- CRITICAL for PythonAnywhere ---
    # Trust X-Forwarded-* from the reverse proxy so:
    #   - request.remote_addr = real client IP (for activation logging)
    #   - request.is_secure = True under HTTPS
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,        # X-Forwarded-For
        x_proto=1,      # X-Forwarded-Proto
        x_host=1,       # X-Forwarded-Host
        x_prefix=1,    # X-Forwarded-Prefix
    )

    db.init_app(app)
    with app.app_context():
        db.create_all()  # idempotent — safe on every worker boot

    # --- Jinja filter for date formatting ---
    @app.template_filter('fmt')
    def _fmt(dt):
        if not dt:
            return '—'
        try:
            return dt.strftime('%Y-%m-%d %H:%M')
        except Exception:
            return str(dt)

    # --- Global auth guard (belt-and-suspenders) ---
    PUBLIC_ENDPOINTS = {'auth.login', 'api.health', 'static'}

    @app.before_request
    def _require_login():
        if request.endpoint in PUBLIC_ENDPOINTS:
            return None
        if request.endpoint and request.endpoint.startswith('api.'):
            return None
        if not session.get('user'):
            return redirect(url_for('auth.login', next=request.path))

    # --- Blueprints ---
    from routes.auth       import auth_bp
    from routes.dashboard  import dashboard_bp
    from routes.products   import products_bp
    from routes.licenses   import licenses_bp
    from routes.api        import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp,  url_prefix='/products')
    app.register_blueprint(licenses_bp,   url_prefix='/licenses')
    app.register_blueprint(api_bp,        url_prefix='/api/v1')

    @app.context_processor
    def inject_globals():
        return {'app_name': 'License Manager'}

    return app


app = create_app()


@app.cli.command('initdb')
def initdb_cmd():
    """Re-apply schema from models (idempotent)."""
    with app.app_context():
        db.create_all()
    click.echo('DB tables ensured.')


@app.cli.command('create-product')
@click.option('--name', required=True)
@click.option('--prefix', required=True)
def create_product(name, prefix):
    from repositories import products
    pid = products.create_product(name, prefix, '', '1.0')
    click.echo(f'Created product id={pid} prefix={prefix.upper()}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,
            debug=os.environ.get('FLASK_DEBUG', '0') == '1')