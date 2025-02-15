import os
import requests
import tkinter as tk
from tkinter import messagebox

class Updater:
    def __init__(self, current_version, repo, exe_name):
        self.current_version = current_version
        self.repo = repo
        self.exe_name = exe_name

    # Get latest release from Github
    def get_latest_version(self):
        url = f"https://api.github.com/repos/{self.repo}/releases/latest"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data["tag_name"]  # Extract version from release tag
        except requests.RequestException as e:
            print(f"Error checking for updates: {e}")
            return None
    # Download and replace exe with new release
    def update_exe(self, version):
        download_url = f"https://github.com/{self.repo}/releases/download/{version}/{self.exe_name}"
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            # Download the new exe in chunks by writing to file
            with open(self.exe_name, "wb") as file: # write-binary
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            messagebox.showinfo("Update Complete", "The application has been updated. Restart required.")
            os.execv(self.exe_name, [self.exe_name])  # Restart the app with new exe
        except requests.RequestException as e:
            messagebox.showerror("Update Failed", f"Failed to download the update: {e}")

    # Check for version update
    def check_for_updates(self):
        latest_version = self.get_latest_version()
        if latest_version and latest_version != self.current_version:
            result = messagebox.askyesno("Update Available",
                                         f"A new version ({latest_version}) is available.\nDo you want to update?")
            if result:
                self.update_exe(latest_version)
        else:
            messagebox.showinfo("No Updates Available", "You're already running the latest version.")
