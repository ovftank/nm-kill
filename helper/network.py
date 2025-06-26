from scapy.all import conf
from scapy.arch import get_if_addr
from scapy.arch.windows import get_windows_if_list


def get_proper_interface(gateway_ip):
    try:
        network_parts = gateway_ip.split('.')
        ip_prefix = '.'.join(network_parts[:3]) + '.'

        for iface in get_windows_if_list():
            for addr in iface.get("ips", []):
                if addr.startswith(ip_prefix):
                    iface_name = iface["name"]
                    return iface_name

        return conf.iface

    except Exception:
        return conf.iface


def get_default_gateway():
    try:
        gateway_ip = conf.route.route("0.0.0.0")[2]
        return gateway_ip if gateway_ip != "0.0.0.0" else None
    except Exception:
        return "192.168.1.1"


def get_current_ip():
    try:
        return get_if_addr(conf.iface)
    except Exception:
        return None
