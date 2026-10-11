import secrets
import string
import re

# Remove visually ambiguous chars: 0/O, 1/I
ALPHABET = ''.join(c for c in (string.ascii_uppercase + string.digits)
                   if c not in '01OI')

def generate_key(prefix: str, group_size: int = 4, groups: int = 3) -> str:
    """Generate a license key like OPTI-7F92-A821-93KD."""
    prefix = prefix.upper()
    parts = [prefix]
    for _ in range(groups):
        parts.append(''.join(secrets.choice(ALPHABET) for _ in range(group_size)))
    return '-'.join(parts)

def is_valid_format(key: str, prefix: str) -> bool:
    pattern = rf'^{prefix.upper()}-[A-Z2-9]{{{4}}}-[A-Z2-9]{{{4}}}-[A-Z2-9]{{{4}}}$'
    return re.match(pattern, key) is not None