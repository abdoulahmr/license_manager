import requests
from flask import current_app, has_app_context

def lookup_geo(ip: str) -> dict:
    if not has_app_context() or not current_app.config.get('GEOIP_ENABLED'):
        return {}
    if not ip or ip.startswith(('10.', '192.168.', '172.16.', '172.17.', '172.18.',
                                '172.19.', '172.20.', '172.21.', '172.22.',
                                '172.23.', '172.24.', '172.25.', '172.26.',
                                '172.27.', '172.28.', '172.29.', '172.30.',
                                '172.31.', '127.')):
        return {}
    try:
        r = requests.get(f'http://ip-api.com/json/{ip}', timeout=3)
        d = r.json()
        if d.get('status') != 'success':
            return {}
        return {
            'isp_org':  d.get('isp', ''),
            'city':     d.get('city', ''),
            'region':   d.get('regionName', ''),
            'country':  d.get('countryCode', ''),
            'coords':   f"{d.get('lat')},{d.get('lon')}",
            'timezone': d.get('timezone', ''),
        }
    except Exception:
        return {}