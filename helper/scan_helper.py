from typing import List, TypedDict

from scapy.all import conf, srp
from scapy.layers.l2 import ARP, Ether


class Device(TypedDict):
    ip: str
    mac: str


def scan_devices() -> List[Device]:
    devices: List[Device] = []

    try:
        gateway_ip = conf.route.route("0.0.0.0")[2]
        if gateway_ip and gateway_ip != "0.0.0.0":
            network_parts = gateway_ip.split('.')
            network_range = f"{network_parts[0]}.{network_parts[1]}.{network_parts[2]}.0/24"
        else:
            network_range = "192.168.1.0/24"

        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") /
                     ARP(pdst=network_range), timeout=2, verbose=0, retry=1)
        for _, received in ans:
            ip = received[ARP].psrc
            mac = received[Ether].src
            devices.append({'ip': ip, 'mac': mac})

        return devices

    except Exception:
        return []
