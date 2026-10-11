from sqlalchemy import select, func, case
from extensions import db
from models import Product, License


def list_products():
    """Return products with license counts as plain dicts (for template convenience)."""
    stmt = (
        select(
            Product,
            func.count(License.id).label('license_count'),
            func.coalesce(
                func.sum(case((License.status == 'active', 1), else_=0)), 0
            ).label('active_count'),
        )
        .outerjoin(License, License.product_id == Product.id)
        .group_by(Product.id)
        .order_by(Product.created_at.desc())
    )
    rows = db.session.execute(stmt).all()
    return [
        {
            'id':            p.id,
            'name':          p.name,
            'code_prefix':   p.code_prefix,
            'description':   p.description,
            'version':       p.version,
            'created_at':    p.created_at,
            'updated_at':    p.updated_at,
            'license_count': cnt,
            'active_count':  int(active),
        }
        for p, cnt, active in rows
    ]


def get_product(product_id):
    return db.session.get(Product, product_id)


def create_product(name, code_prefix, description='', version='1.0'):
    p = Product(name=name, code_prefix=code_prefix.upper(),
                description=description, version=version)
    db.session.add(p)
    db.session.commit()
    return p.id


def update_product(product_id, name, code_prefix, description, version):
    p = get_product(product_id)
    if not p:
        return None
    p.name = name
    p.code_prefix = code_prefix.upper()
    p.description = description
    p.version = version
    db.session.commit()
    return p


def delete_product(product_id):
    p = get_product(product_id)
    if p:
        db.session.delete(p)
        db.session.commit()