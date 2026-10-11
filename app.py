import os
import click
from flask import Flask
from config import Config
from extensions import db
from models import Product, License, Activation


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init SQLAlchemy
    db.init_app(app)

    # Create tables on first request (idempotent)
    with app.app_context():
        db.create_all()

    # Jinja filter for safe date rendering
    @app.template_filter('fmt')
    def _fmt(dt):
        if not dt:
            return '—'
        try:
            return dt.strftime('%Y-%m-%d %H:%M')
        except Exception:
            return str(dt)

    # Blueprints
    from routes.auth       import auth_bp
    from routes.dashboard  import dashboard_bp
    from routes.products   import products_bp
    from routes.licenses   import licenses_bp
    from routes.api        import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(licenses_bp, url_prefix='/licenses')
    app.register_blueprint(api_bp,      url_prefix='/api/v1')

    @app.context_processor
    def inject_globals():
        return {'app_name': 'License Manager'}

    return app


app = create_app()


@app.cli.command('initdb')
def initdb_cmd():
    """Re-create tables from models (idempotent)."""
    with app.app_context():
        db.create_all()
    click.echo('DB tables ensured.')


@app.cli.command('create-product')
@click.option('--name')
@click.option('--prefix')
def create_product(name, prefix):
    from repositories import products
    pid = products.create_product(name, prefix, '', '1.0')
    click.echo(f'Created product id={pid} prefix={prefix.upper()}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)