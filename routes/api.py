from functools import wraps
from flask import Blueprint, request, jsonify
from config import Config
from extensions import db
from repositories import licenses, activations
from utils.fingerprint import fingerprint
from utils.geoip import lookup_geo

api_bp = Blueprint('api', __name__)


def require_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify(status='error', reason='missing_token'), 401
        if auth.split(' ', 1)[1] != Config.API_TOKEN:
            return jsonify(status='error', reason='invalid_token'), 403
        return f(*args, **kwargs)
    return wrap


@api_bp.route('/health')
def health():
    return jsonify(status='ok')


@api_bp.route('/licenses/activate', methods=['POST'])
@require_token
def activate():
    data    = request.get_json(silent=True) or {}
    key     = data.get('license_key')
    machine = data.get('machine') or {}

    if not key or not machine:
        return jsonify(status='error', reason='missing_fields'), 400

    lic = licenses.get_license_by_key(key)
    if not lic:
        return jsonify(status='error', reason='not_found'), 404

    if lic.status == 'revoked':
        activations.log_activation(lic.id, 'activate', machine, success=False,
                                   reason='revoked',
                                   geo=lookup_geo(machine.get('public_ip')))
        return jsonify(status='error', reason='revoked'), 403

    fp = fingerprint(machine)
    public_ip = (machine.get('public_ip')
                 or request.headers.get('X-Forwarded-For', '').split(',')[0].strip())
    geo = lookup_geo(public_ip)

    if lic.status == 'pending':
        licenses.activate(lic.id, fp)
        activations.log_activation(lic.id, 'activate', machine, success=True, geo=geo)
        return jsonify(status='ok', license_status='active',
                        product_id=lic.product_id), 200

    # Already active — verify fingerprint
    if lic.machine_fingerprint != fp:
        activations.log_activation(lic.id, 'check', machine, success=False,
                                   reason='machine_mismatch', geo=geo)
        return jsonify(status='error', reason='machine_mismatch'), 403

    activations.log_activation(lic.id, 'check', machine, success=True, geo=geo)
    return jsonify(status='ok', license_status='active'), 200


@api_bp.route('/licenses/verify', methods=['POST'])
@require_token
def verify():
    data    = request.get_json(silent=True) or {}
    key     = data.get('license_key')
    machine = data.get('machine') or {}

    if not key:
        return jsonify(status='error', reason='missing_key'), 400

    lic = licenses.get_license_by_key(key)
    if not lic:
        return jsonify(status='error', reason='not_found'), 404

    status = lic.status
    if status == 'active' and machine and lic.machine_fingerprint:
        if lic.machine_fingerprint != fingerprint(machine):
            status = 'mismatch'

    return jsonify(
        status='ok',
        license_status=status,
        customer=lic.customer_name,
        type=lic.license_type,
    ), 200


@api_bp.route('/licenses/status', methods=['GET'])
@require_token
def status():
    key = request.args.get('key')
    if not key:
        return jsonify(status='error', reason='missing_key'), 400
    lic = licenses.get_license_by_key(key)
    if not lic:
        return jsonify(status='error', reason='not_found'), 404
    return jsonify(
        status='ok',
        license_key=lic.license_key,
        license_status=lic.status,
        customer=lic.customer_name,
        type=lic.license_type,
        activated_at=lic.activated_at.isoformat() if lic.activated_at else None,
    ), 200