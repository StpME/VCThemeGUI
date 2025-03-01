import os
import requests
from tkinter import messagebox


class Updater:
    """
    A class for fetching and deploying updates for the program.
    """
    def __init__(self, current_version, repo, exe_name):
        """
        Initialize the Updater with the current version, repository,
        and executable name.

        Args:
            current_version (string): The current version of the program.
            repo (string): The Github repository author and project name.
            exe_name (string): The name of the executable file.
        """
        self.current_version = current_version
        self.repo = repo
        self.exe_name = exe_name

    def get_latest_version(self):
        """
        Retrieve the latest release version from the Github repository.

        Returns:
            (string): The latest version release tag.
            None if an error occurs.
        """
        url = f"https://api.github.com/repos/{self.repo}/releases/latest"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data["tag_name"]  # Extract version from release tag
        except requests.RequestException as e:
            print(f"Error checking for updates: {e}")
            return None

    def update_exe(self, version):
        """
        Download the new release executable and replace the current one.
        Pulls download from latest tagged release on Github page.

        Args:
            version (string): The version number to download and install.
        """
        download_url = f"https://github.com/{self.repo}/releases/download/"
        f"{version}/{self.exe_name}"
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            # Download the new exe in chunks by writing to file
            with open(self.exe_name, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            messagebox.showinfo(
                "Update Complete",
                "The application has been updated. Restart required.")
            # Restart the app with new exe
            os.execv(self.exe_name, [self.exe_name])
        except requests.RequestException as e:
            messagebox.showerror("Update Failed",
                                 f"Failed to download the update: {e}")

    def check_for_updates(self):
        """
        Check for updates by comparing version numbers and
        prompts the user to update if available.
        """
        latest_version = self.get_latest_version()
        if latest_version and latest_version != self.current_version:
            result = messagebox.askyesno(
                "Update Available",
                f"A new version ({latest_version}) is available.\n"
                "Do you want to update?")
            if result:
                self.update_exe(latest_version)
        else:
            messagebox.showinfo("No Updates Available",
                                "You're already running the latest version.")
