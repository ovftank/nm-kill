import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, TypedDict


class Device(TypedDict):
    ip: str
    mac: str


def get_network_prefix():
    try:
        current_ip = subprocess.check_output(
            "ipconfig | findstr /i \"IPv4\"",
            shell=True,
            universal_newlines=True
        )

        for line in current_ip.splitlines():
            if "192.168." in line:
                ip_parts = re.search(r"(\d+\.\d+\.\d+\.)\d+", line)
                if ip_parts:
                    return ip_parts.group(1)
    except Exception:
        pass
    return None


def ping_ip(ip):
    try:
        subprocess.call(
            ["ping", "-n", "1", "-w", "300", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass


def scan_devices() -> List[Device]:
    devices: List[Device] = []

    try:
        ip_base = get_network_prefix()
        if not ip_base:
            return devices

        ips_to_scan = [f"{ip_base}{i}" for i in range(1, 255)]

        with ThreadPoolExecutor(max_workers=30) as executor:
            list(executor.map(ping_ip, ips_to_scan))

        time.sleep(0.3)

        arp_output = subprocess.check_output(
            ["arp", "-a"],
            universal_newlines=True
        )
        pattern = r"(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2})\s+(\w+)"

        for line in arp_output.splitlines():
            match = re.search(pattern, line)
            if match:
                ip = match.group(1)
                mac = match.group(2).replace('-', ':').upper()
                type_entry = match.group(3).lower()

                if type_entry == "dynamic":
                    devices.append({'ip': ip, 'mac': mac})

    except Exception:
        pass

    return devices
