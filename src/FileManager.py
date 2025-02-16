import sys
import os

class FileManager:
    def __init__(self):
        pass
    
    # Dynamic relative path finder for exe distribution
    def file_path(self, relative_path):
        if getattr(sys, 'frozen', False):  # Check if exe
            base_path = sys._MEIPASS # temp dir
        else:  # Otherwise script for dev
            base_path = os.path.dirname(os.path.abspath(__file__)) # wd of script
        return os.path.join(base_path, relative_path) # create full path dependent on base
    




    