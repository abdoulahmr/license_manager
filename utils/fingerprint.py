import hashlib

def fingerprint(machine: dict) -> str:
    """Stable machine fingerprint. Excludes volatile fields (IPs, geo)."""
    raw = '|'.join([
        str(machine.get('hostname', '')).lower(),
        str(machine.get('mac_address', '')).lower(),
        str(machine.get('processor', '')).lower(),
        str(machine.get('architecture', '')).lower(),
        str(machine.get('os_info', '')).lower(),
    ])
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()