import os
import subprocess
import tempfile
import threading
from tkinter import messagebox
from typing import Any, Dict, Optional

import requests
from packaging import version

from version import __version__


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
            try:
                download_url = self.get_download_url()
                if not download_url:
                    messagebox.showerror("Error", "File not found!")
                    return

                messagebox.showinfo("Download", "Downloading...")

                installer_path = self.download_update(download_url)
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
                messagebox.showerror("Error", f"Failed: {str(e)}")

        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()


update_checker = UpdateChecker()
