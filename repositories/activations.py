from sqlalchemy import select, func, case
from extensions import db
from models import Activation, License, Product


def list_for_license(license_id):
    stmt = (
        select(Activation)
        .where(Activation.license_id == license_id)
        .order_by(Activation.created_at.desc())
    )
    return db.session.execute(stmt).scalars().all()


def log_activation(license_id, event_type, machine, success=True,
                   reason=None, geo=None):
    geo = geo or {}
    a = Activation(
        license_id   = license_id,
        event_type   = event_type,
        hostname     = machine.get('hostname'),
        os_info      = machine.get('os_info'),
        os_version   = machine.get('os_version'),
        architecture = machine.get('architecture'),
        processor    = machine.get('processor'),
        local_ip     = machine.get('local_ip'),
        mac_address  = machine.get('mac_address'),
        public_ip    = machine.get('public_ip'),
        isp_org      = geo.get('isp_org'),
        city         = geo.get('city'),
        region       = geo.get('region'),
        country      = geo.get('country'),
        coordinates  = geo.get('coords'),
        timezone     = geo.get('timezone'),
        success      = success,
        reason       = reason,
    )
    db.session.add(a)
    db.session.commit()
    return a


def recent(limit=20):
    stmt = (
        select(Activation, License, Product)
        .join(License,  License.id  == Activation.license_id)
        .join(Product,  Product.id  == License.product_id)
        .order_by(Activation.created_at.desc())
        .limit(limit)
    )
    rows = db.session.execute(stmt).all()
    return [
        {
            **a.__dict__,
            'license_key':   l.license_key,
            'customer_name': l.customer_name,
            'product_name':  p.name,
        }
        for a, l, p in rows
    ]


def by_country(days=30):
    from datetime import datetime, timedelta
    since = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(Activation.country, func.count().label('cnt'))
        .where(Activation.country.isnot(None))
        .where(Activation.created_at > since)
        .group_by(Activation.country)
        .order_by(func.count().desc())
        .limit(10)
    )
    return [{'country': c, 'count': n} for c, n in db.session.execute(stmt).all()]


def counts():
    from sqlalchemy import literal_column
    p_cnt = db.session.execute(select(func.count()).select_from(Product)).scalar() or 0
    l_cnt = db.session.execute(select(func.count()).select_from(License)).scalar() or 0
    a_cnt = db.session.execute(select(func.count()).select_from(Activation)).scalar() or 0
    active   = db.session.execute(select(func.count()).select_from(License).where(License.status == 'active')).scalar() or 0
    pending  = db.session.execute(select(func.count()).select_from(License).where(License.status == 'pending')).scalar() or 0
    revoked  = db.session.execute(select(func.count()).select_from(License).where(License.status == 'revoked')).scalar() or 0
    failed   = db.session.execute(select(func.count()).select_from(Activation).where(Activation.success == False)).scalar() or 0
    return {
        'products':    p_cnt,
        'licenses':    l_cnt,
        'active':      active,
        'pending':     pending,
        'revoked':     revoked,
        'activations': a_cnt,
        'failed':      failed,
    }


def timeseries(days=30):
    from datetime import datetime, timedelta
    since = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(
            func.date(Activation.created_at).label('day'),
            func.count().label('cnt'),
        )
        .where(Activation.created_at > since)
        .group_by(func.date(Activation.created_at))
        .order_by(func.date(Activation.created_at))
    )
    return [{'day': d, 'count': n} for d, n in db.session.execute(stmt).all()]