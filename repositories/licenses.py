from sqlalchemy import select
from extensions import db
from models import License, Product
from utils.license_key import generate_key


def list_licenses():
    stmt = (
        select(License, Product)
        .join(Product, Product.id == License.product_id)
        .order_by(License.created_at.desc())
    )
    rows = db.session.execute(stmt).all()
    return [
        {
            **l.__dict__,
            'product_name': p.name,
            'code_prefix':  p.code_prefix,
        }
        for l, p in rows
    ]


def get_license(license_id):
    stmt = (
        select(License, Product)
        .join(Product, Product.id == License.product_id)
        .where(License.id == license_id)
    )
    row = db.session.execute(stmt).first()
    if not row:
        return None
    lic, prod = row
    return {
        **lic.__dict__,
        'product_name': prod.name,
        'code_prefix':  prod.code_prefix,
    }


def get_license_by_key(key):
    return db.session.execute(
        select(License).where(License.license_key == key)
    ).scalar_one_or_none()


def create_license(product_id, customer_name, customer_email='',
                   license_type='Professional', notes=''):
    product = db.session.get(Product, product_id)
    if not product:
        raise ValueError('Unknown product')

    # Generate a unique key (10 attempts)
    for _ in range(10):
        key = generate_key(product.code_prefix)
        exists = db.session.execute(
            select(License.id).where(License.license_key == key)
        ).first()
        if not exists:
            break
    else:
        raise RuntimeError('Could not generate unique license key')

    lic = License(
        product_id=product_id,
        license_key=key,
        customer_name=customer_name,
        customer_email=customer_email,
        license_type=license_type,
        notes=notes,
    )
    db.session.add(lic)
    db.session.commit()
    return lic.id, key


def update_license(license_id, customer_name, customer_email,
                   license_type, notes, status):
    lic = db.session.get(License, license_id)
    if not lic:
        return None
    lic.customer_name  = customer_name
    lic.customer_email = customer_email
    lic.license_type   = license_type
    lic.notes          = notes
    lic.status         = status
    db.session.commit()
    return lic


def delete_license(license_id):
    lic = db.session.get(License, license_id)
    if lic:
        db.session.delete(lic)
        db.session.commit()


def reset_activation(license_id):
    lic = db.session.get(License, license_id)
    if not lic:
        return
    lic.status = 'pending'
    lic.machine_fingerprint = None
    lic.activated_at = None
    db.session.commit()


def revoke_license(license_id):
    lic = db.session.get(License, license_id)
    if lic:
        lic.status = 'revoked'
        db.session.commit()


def activate(license_id, fingerprint):
    lic = db.session.get(License, license_id)
    if not lic:
        return None
    lic.status = 'active'
    lic.machine_fingerprint = fingerprint
    from datetime import datetime
    lic.activated_at = datetime.utcnow()
    db.session.commit()
    return lic