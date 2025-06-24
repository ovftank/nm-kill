import re
import subprocess
from typing import List, TypedDict


class Device(TypedDict):
    ip: str
    mac: str


def scan_devices() -> List[Device]:
    devices: List[Device] = []
    try:
        arp_output = subprocess.check_output(
            ["arp", "-a"],
            universal_newlines=True
        )
        pattern = r"(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2})"

        for line in arp_output.splitlines():
            match = re.search(pattern, line)
            if match:
                ip = match.group(1)
                mac = match.group(2).replace('-', ':').upper()
                devices.append({'ip': ip, 'mac': mac})
    except Exception:
        pass
    return devices
