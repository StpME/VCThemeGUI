import os
import tempfile
import requests
from tkinter import messagebox


class Updater:
    """
    A class for fetching and deploying updates for the program.
    """
    def __init__(self, current_version, repo, exe_name, root):
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
        self.root = root

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
        Runs a temporary batch script to handle the update process.
        Pulls download from latest tagged release on Github page.

        Args:
            version (string): The version number to download and install.
        """
        versioned_new_name = f"{self.exe_name}_{version}.exe"
        download_url = (f"https://github.com/{self.repo}/releases/download/"
                        f"{version}/{versioned_new_name}")

        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # Download the new exe to a temporary file
            temp_dir = tempfile.gettempdir()
            temp_exe = os.path.join(temp_dir, f"{self.exe_name}_temp.exe")
            with open(temp_exe, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            # Create a temporary batch script to handle the update
            bat_script = os.path.join(temp_dir, "update.bat")
            current_exe = os.path.join(
                os.getcwd(),
                f"{self.exe_name}_{self.current_version}.exe")
            new_exe = os.path.join(os.getcwd(), versioned_new_name)

            with open(bat_script, "w") as bat_file:
                bat_file.write(f"""
                @echo off
                REM Wait for the main program to exit
                timeout /t 2 /nobreak >nul

                REM Rename the current executable to a temporary name
                ren "{current_exe}" "{self.exe_name}_old.exe"

                REM Move the new executable to the correct location
                move "{temp_exe}" "{new_exe}"

                REM Start the new executable
                start "" "{new_exe}"

                REM Delete the old executable
                del "{os.path.join(os.getcwd(), f"{self.exe_name}_old.exe")}"

                REM Delete the batch script itself
                del "{bat_script}"
                """)

            # Launch the batch script
            os.startfile(bat_script)

            # Close the current application
            self.root.destroy()

        except requests.RequestException as e:
            messagebox.showerror("Update Failed",
                                 f"Failed to download the update: {e}")
        except Exception as e:
            messagebox.showerror("Update Failed",
                                 f"An error occurred during the update: {e}")

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
