import os
import subprocess

import requests


def check_npcap_exists():
    return os.path.exists("C:\\Windows\\SysWOW64\\Npcap")


def install_npcap():
    try:
        url = requests.get("https://npcap.com/dist/npcap-1.82.exe")
        npcap_file_name = "npcap-1.82.exe"
        open(f"{npcap_file_name}", 'wb').write(url.content)
        subprocess.run(
            [npcap_file_name, "/winpcap_mode=yes", "/dot11_support=yes"],
            shell=True,
            check=False)
        os.remove(npcap_file_name)
        return True
    except Exception:
        return False
