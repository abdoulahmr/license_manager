from datetime import datetime
from extensions import db


class Product(db.Model):
    __tablename__ = 'products'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(120), nullable=False)
    code_prefix = db.Column(db.String(8),   nullable=False, unique=True)
    description = db.Column(db.Text)
    version     = db.Column(db.String(32),  default='1.0')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow,
                            onupdate=datetime.utcnow, nullable=False)

    licenses = db.relationship(
        'License',
        backref='product',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def __repr__(self):
        return f'<Product {self.code_prefix} {self.name}>'


class License(db.Model):
    __tablename__ = 'licenses'

    id                  = db.Column(db.Integer, primary_key=True)
    product_id          = db.Column(
        db.Integer,
        db.ForeignKey('products.id', ondelete='CASCADE'),
        nullable=False, index=True,
    )
    license_key         = db.Column(db.String(64), nullable=False, unique=True, index=True)
    customer_name       = db.Column(db.String(255), nullable=False)
    customer_email      = db.Column(db.String(255))
    license_type        = db.Column(db.String(64), default='Professional', nullable=False)
    status              = db.Column(db.String(16),  default='pending', nullable=False)  # pending|active|revoked
    machine_fingerprint = db.Column(db.String(64))
    activated_at        = db.Column(db.DateTime)
    max_activations     = db.Column(db.Integer, default=1, nullable=False)
    notes               = db.Column(db.Text)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow,
                                    onupdate=datetime.utcnow, nullable=False)

    activations = db.relationship(
        'Activation',
        backref='license',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def __repr__(self):
        return f'<License {self.license_key} [{self.status}]>'


class Activation(db.Model):
    __tablename__ = 'activations'

    id            = db.Column(db.Integer, primary_key=True)
    license_id    = db.Column(
        db.Integer,
        db.ForeignKey('licenses.id', ondelete='CASCADE'),
        nullable=False, index=True,
    )
    event_type    = db.Column(db.String(16), nullable=False)   # activate|check|revoke|reset
    hostname      = db.Column(db.String(255))
    os_info       = db.Column(db.String(255))
    os_version    = db.Column(db.String(255))
    architecture  = db.Column(db.String(32))
    processor     = db.Column(db.String(255))
    local_ip      = db.Column(db.String(64))
    mac_address   = db.Column(db.String(32))
    public_ip     = db.Column(db.String(64))
    isp_org       = db.Column(db.String(255))
    city          = db.Column(db.String(128))
    region        = db.Column(db.String(128))
    country       = db.Column(db.String(8))
    coordinates   = db.Column(db.String(64))
    timezone      = db.Column(db.String(64))
    success       = db.Column(db.Boolean, default=True, nullable=False)
    reason        = db.Column(db.String(255))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f'<Activation {self.event_type} ok={self.success}>'