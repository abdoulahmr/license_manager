"""
Reference client SDK. Drop into your application and call LicenseClient.activate(key).
"""
import socket
import platform
import uuid
import re
import requests

class LicenseClient:
    def __init__(self, server_url: str, api_token: str):
        self.server_url = server_url.rstrip('/')
        self.api_token = api_token

    def collect_machine_info(self) -> dict:
        mac = ':'.join(re.findall('..', uuid.getnode().hex(0).rjust(12, '0')))
        try:
            hostname = socket.gethostname()
        except Exception:
            hostname = 'unknown'

        public_ip = None
        try:
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
        except Exception:
            pass

        return {
            'hostname':    hostname,
            'os_info':     platform.system(),
            'os_version':  platform.version(),
            'architecture':platform.machine(),
            'processor':   platform.processor() or platform.machine(),
            'local_ip':    socket.gethostbyname(socket.gethostname()),
            'mac_address': mac,
            'public_ip':   public_ip,
        }

    def activate(self, license_key: str) -> dict:
        machine = self.collect_machine_info()
        r = requests.post(
            f'{self.server_url}/api/v1/licenses/activate',
            json={'license_key': license_key, 'machine': machine},
            headers={'Authorization': f'Bearer {self.api_token}'},
            timeout=10,
        )
        return r.json(), r.status_code

    def verify(self, license_key: str) -> dict:
        machine = self.collect_machine_info()
        r = requests.post(
            f'{self.server_url}/api/v1/licenses/verify',
            json={'license_key': license_key, 'machine': machine},
            headers={'Authorization': f'Bearer {self.api_token}'},
            timeout=10,
        )
        return r.json(), r.status_code

    def status(self, license_key: str) -> dict:
        r = requests.get(
            f'{self.server_url}/api/v1/licenses/status',
            params={'key': license_key},
            headers={'Authorization': f'Bearer {self.api_token}'},
            timeout=10,
        )
        return r.json(), r.status_code

# ----- example usage -----
if __name__ == '__main__':
    client = LicenseClient('http://localhost:5000', 'dev-api-token-change-me')
    print(client.activate('OPTI-XXXX-XXXX-XXXX'))   # replace with real key