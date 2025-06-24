import subprocess

from scapy.arch.windows import get_windows_if_list


def get_default_gateway():
    try:
        output = subprocess.check_output(
            "ipconfig | findstr /i gateway",
            shell=True,
            universal_newlines=True
        )
        for line in output.splitlines():
            parts = line.split(":")
            if len(parts) > 1 and parts[1].strip():
                return parts[1].strip()
    except Exception:
        pass
    return "192.168.1.1"


def get_default_iface():
    try:
        ifaces = get_windows_if_list()
        if not ifaces:
            return None

        for iface in ifaces:
            if iface['ips'] and iface['ips'] != []:
                return iface['name']
    except Exception as e:
        print(f"Lỗi khi lấy interface mặc định: {e}")
    return None


def get_mac_from_ip(ip):
    try:
        arp_output = subprocess.check_output(
            ["arp", "-a", ip],
            universal_newlines=True
        )
        for line in arp_output.splitlines():
            if ip in line:
                parts = line.split()
                if len(parts) >= 2:
                    return parts[1].replace('-', ':').upper()
    except Exception:
        pass
    return None


def get_my_mac():
    try:
        output = subprocess.check_output(
            "ipconfig /all", shell=True, universal_newlines=True)
        for line in output.splitlines():
            if "Physical Address" in line:
                mac = line.split(":")[-1].strip().replace("-", ":")
                return mac.upper()
    except Exception:
        pass
    return None


def get_current_ip():
    try:
        output = subprocess.check_output(
            "ipconfig", shell=True, universal_newlines=True)
        for line in output.splitlines():
            if "IPv4 Address" in line and "192.168." in line:
                ip = line.split(":")[-1].strip()
                return ip
    except Exception:
        pass
    return None
