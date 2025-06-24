import os
import subprocess
import tempfile
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, Optional

import requests
from packaging import version

from version import __version__


class ProgressDialog:
    def __init__(self, title="Download Progress"):
        self.root = tk.Toplevel()
        self.root.title(title)
        self.root.geometry("400x150")
        self.root.resizable(False, False)
        self.root.transient()
        self.root.grab_set()

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (150 // 2)
        self.root.geometry(f"400x150+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        self.setup_widgets()

    def setup_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(main_frame, text="Preparing download...")
        self.status_label.pack(pady=(0, 10))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=350
        )
        self.progress_bar.pack(pady=(0, 10))

        self.percent_label = ttk.Label(main_frame, text="0%")
        self.percent_label.pack()

    def update_progress(self, progress, status=None):
        self.progress_var.set(progress)
        self.percent_label.config(text=f"{progress:.1f}%")
        if status:
            self.status_label.config(text=status)
        self.root.update()

    def close(self):
        self.root.destroy()


class UpdateChecker:
    def __init__(self):
        self.repo_owner = "ovftank"
        self.repo_name = "nm-kill"
        self.current_version = __version__
        self.github_api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"

    def get_latest_release(self) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def is_update_available(self) -> tuple[bool, Optional[str]]:
        latest_release = self.get_latest_release()
        if not latest_release:
            return False, None

        latest_version = latest_release.get("tag_name", "").lstrip("v")
        if not latest_version:
            return False, None

        try:
            return version.parse(latest_version) > version.parse(self.current_version), latest_version
        except Exception:
            return False, None

    def get_download_url(self) -> Optional[str]:
        latest_release = self.get_latest_release()
        if not latest_release:
            return None

        assets = latest_release.get("assets", [])
        for asset in assets:
            if asset.get("name") == "nm-kill-setup.exe":
                return asset.get("browser_download_url")
        return None

    def download_update(self, download_url: str, progress_callback=None) -> Optional[str]:
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, "nm-kill-setup-update.exe")

            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)

            return temp_file
        except Exception:
            return None

    def install_update(self, installer_path: str) -> bool:
        try:
            subprocess.Popen([installer_path, "/SILENT"], shell=True)
            return True
        except Exception:
            return False

    def check_and_prompt_update(self):
        def check_update_thread():
            try:
                is_available, latest_ver = self.is_update_available()
                if not is_available:
                    messagebox.showinfo("Update", "Latest version!")
                    return

                result = messagebox.askyesno(
                    "Update",
                    f"v{latest_ver} available!\nCurrent: v{self.current_version}\n\nUpdate?"
                )

                if result:
                    self.download_and_install()

            except Exception as e:
                messagebox.showerror("Error", f"Check failed: {str(e)}")

        thread = threading.Thread(target=check_update_thread, daemon=True)
        thread.start()

    def download_and_install(self):
        def download_thread():
            progress_dialog = None
            try:
                download_url = self.get_download_url()
                if not download_url:
                    messagebox.showerror("Error", "File not found!")
                    return

                progress_dialog = ProgressDialog("Downloading Update")
                progress_dialog.update_progress(0, "Starting download...")

                def progress_callback(progress):
                    if progress_dialog:
                        progress_dialog.update_progress(
                            progress, f"Downloading... {progress:.1f}%")

                installer_path = self.download_update(
                    download_url, progress_callback)

                if progress_dialog:
                    progress_dialog.update_progress(100, "Download complete!")
                    progress_dialog.close()
                    progress_dialog = None

                if not installer_path:
                    messagebox.showerror("Error", "Download failed!")
                    return

                result = messagebox.askyesno(
                    "Install",
                    "Download complete!\nApp will close.\n\nContinue?"
                )

                if result:
                    if self.install_update(installer_path):
                        os._exit(0)
                    else:
                        messagebox.showerror("Error", "Install failed!")

            except Exception as e:
                if progress_dialog:
                    progress_dialog.close()
                messagebox.showerror("Error", f"Failed: {str(e)}")

        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()


update_checker = UpdateChecker()
