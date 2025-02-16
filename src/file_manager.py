import sys
import os
from image_preview import ImagePreview

class FileManager:
    def __init__(self, config):
        self.theme_config = config
    
    # Dynamic relative path finder for exe distribution
    def file_path(self, relative_path):
        if getattr(sys, 'frozen', False):  # Check if exe
            base_path = sys._MEIPASS # temp dir
        else:  # Otherwise script for dev
            base_path = os.path.dirname(os.path.abspath(__file__)) # wd of script
        return os.path.join(base_path, relative_path) # create full path dependent on base
    
    # Read CSS file and extract image URLs
    def extract_urls(self, file_path):
        try:
            with open(file_path, "r") as file:
                css_content = file.read()
                img_urls = ImagePreview.extract_image_urls(css_content, self.theme_config[2])
                return css_content, img_urls
        except Exception as e:
            print(f"Error reading CSS file: {e}")
            return None, []
    
    def get_version(self):
        # Read current version num from txt or return default version if missing/error
        version_file_path = self.file_path("version.txt")
        try:
            with open(version_file_path, "r") as version_file:
                return version_file.read().strip()
        except FileNotFoundError:
            print(f"Warning: version.txt not found. Using default version: v1.0.0")
            return "v1.0.0"



    