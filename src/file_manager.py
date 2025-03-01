import sys
import os
from image_preview import ImagePreview


class FileManager:
    """
    Manages file operations for the program,
    such as versioning and file data extraction.
    """
    def __init__(self, config):
        """
        Initialize the FileManager with theme configuration.

        Args:
            config (list): Contains theme specific configuration details.
        """
        self.theme_config = config

    def file_path(self, relative_path):
        """
        Resolve the absolute path for a given relative path.

        Dynamically determines the base path depending on whether
        the program is running as a script or a frozen executable
        (Development vs distribution).

        Args:
            relative_path (string): The relative path to resolve.

        Returns:
            (string): The absolute path.
        """
        if getattr(sys, 'frozen', False):  # Check if exe
            base_path = sys._MEIPASS  # temp dir
        else:  # Otherwise script for development
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def extract_urls(self, file_path):
        """
        Extract image URLs from the selected CSS file.

        Args:
            file_path (str): Path to the CSS file.

        Returns:
            tuple: A tuple containing the CSS content (str)
            and a list of image URLs (list).
            Returns (None, []) if an error occurs (Invalid/unreadable file).
        """
        try:
            with open(file_path, "r") as file:
                css_content = file.read()
                img_urls = ImagePreview.extract_image_urls(
                    css_content, self.theme_config[2])
                return css_content, img_urls
        except Exception as e:
            print(f"Error reading CSS file: {e}")
            return None, []

    def get_version(self):
        """
        Retrieve the current version from a version file,
        otherwise return a set default version.

        Returns:
            (string): The current version or a set default in case of error.
        """
        version_file_path = self.file_path("version.txt")
        try:
            with open(version_file_path, "r") as version_file:
                return version_file.read().strip()
        except FileNotFoundError:
            print("Warning: version.txt not found. Using default version.")
            return "v1.0.0"
