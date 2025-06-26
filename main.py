
import asyncio
import ctypes
import multiprocessing
import os
import re
import subprocess
import sys
import threading
import webbrowser
from tkinter import messagebox
from typing import Optional

import pystray
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from PIL import Image

from helper.arp_helper import arp_spoof
from helper.network import get_current_ip, get_default_gateway
from helper.npcap_helper import check_npcap_exists, install_npcap
from helper.scan_helper import scan_devices
from helper.updater import update_checker
from version import __version__

app = FastAPI(title="NM KILL")

active_sessions = {}


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def request_admin():
    if is_admin():
        return True

    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return False
    except Exception:
        messagebox.showerror("lỗi cmnr", "chạy với quyền admin đi sếp")
        return False


def kill_port_80_processes():
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            check=True
        )

        lines = result.stdout.split('\n')
        pids_to_kill = []

        for line in lines:
            if ':80 ' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids_to_kill.append(pid)

        for pid in pids_to_kill:
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid],
                               capture_output=True, check=False)
            except Exception:
                pass

        return len(pids_to_kill) > 0

    except Exception:
        return False


def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)  # type: ignore
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def create_icon():
    try:
        favicon_path = get_resource_path('static/favicon.ico')
        return Image.open(favicon_path)
    except Exception:
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='black')
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        draw.ellipse([16, 16, 48, 48], fill='white')
        return image


def open_browser():
    webbrowser.open('http://localhost:80')


def check_for_updates(_, __):
    update_checker.check_and_prompt_update()


def quit_app(icon, _):
    icon.stop()


def run_server():
    try:
        if not check_npcap_exists() and not install_npcap():
            messagebox.showerror(
                "lỗi", "lỗi khi cài npcap, tắt app mở lại hoặc cài thủ công(đọc hd trên docs)")
            return

        kill_port_80_processes()

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=80,
            reload=False,
            workers=1,
            access_log=False,
            log_config=None
        )
    except Exception as e:
        messagebox.showerror("lỗi:", f"{str(e)}")


@app.get("/api/gateway")
async def get_gateway():
    loop = asyncio.get_event_loop()
    gateway = await loop.run_in_executor(None, get_default_gateway)
    return {"gateway": gateway}


@app.get("/api/current")
async def get_current():
    loop = asyncio.get_event_loop()
    current_ip = await loop.run_in_executor(None, get_current_ip)
    return {"ip": current_ip}


@app.get("/api/devices")
async def get_devices():
    loop = asyncio.get_event_loop()
    devices = await loop.run_in_executor(None, scan_devices)
    return {"devices": devices}


@app.post("/api/devices/refresh")
async def refresh_devices():
    loop = asyncio.get_event_loop()
    devices = await loop.run_in_executor(None, scan_devices)
    gateway = await loop.run_in_executor(None, get_default_gateway)
    current_ip = await loop.run_in_executor(None, get_current_ip)

    return {"devices": devices, "gateway": gateway, "current": {"ip": current_ip}}


@app.get("/api/sessions")
async def get_sessions():
    return {ip: {"target": s["target"], "gateway": s["gateway"]} for ip, s in active_sessions.items()}


@app.post("/api/spoof")
async def start_spoofing(target_id: int, custom_gateway: Optional[str] = None):
    loop = asyncio.get_event_loop()
    devices = await loop.run_in_executor(None, scan_devices)

    if not devices:
        raise HTTPException(status_code=404)

    if not 0 <= target_id < len(devices):
        raise HTTPException(status_code=400)

    target = devices[target_id]
    gateway_ip = await loop.run_in_executor(None, get_default_gateway)

    if custom_gateway:
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", custom_gateway):
            raise HTTPException(status_code=400)
        gateway_ip = custom_gateway

    if target["ip"] in active_sessions:
        raise HTTPException(status_code=409)

    stop_event = threading.Event()
    spoof_thread = threading.Thread(
        target=arp_spoof, args=(target['ip'], gateway_ip, stop_event))
    spoof_thread.daemon = True
    spoof_thread.start()

    active_sessions[target["ip"]] = {
        "target": target,
        "gateway": gateway_ip,
        "stop_event": stop_event,
        "thread": spoof_thread
    }

    return {}


@app.delete("/api/spoof/{session_id}")
async def stop_spoofing(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404)

    session = active_sessions[session_id]
    session["stop_event"].set()
    session["thread"].join(timeout=5)
    del active_sessions[session_id]

    return {}


@app.get("/api/version")
async def get_version():
    return {"version": __version__}


@app.get("/api/update/check")
async def check_update():
    try:
        is_available, latest_version = update_checker.is_update_available()
        return {
            "current_version": __version__,
            "latest_version": latest_version,
            "update_available": is_available
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


static_dir = get_resource_path('static')
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="spa")


if __name__ == "__main__":
    multiprocessing.freeze_support()

    if not request_admin():
        sys.exit(0)

    favicon_path = get_resource_path('static/favicon.ico')
    update_checker.icon_path = favicon_path

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    icon = pystray.Icon(
        "NM KILL",
        create_icon(),
        menu=pystray.Menu(
            pystray.MenuItem("Open Browser", open_browser),
            pystray.MenuItem("Check for Updates", check_for_updates),
            pystray.MenuItem("Quit", quit_app)
        )
    )
    icon.run()
