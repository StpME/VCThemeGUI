import tkinter as tk
import os
from setup import Setup
from backdrop_manager import BackdropManager
from file_manager import FileManager
from base_gui import BaseGUI


class SoftXGUI(BaseGUI):
    """
    Theme specific class for individual syntax not managed by the base gui.
    Includes methods for extracting and adding backdrops to the CSS file.
    Inherits from the BaseGUI class.
    """
    def __init__(self, root):
        """
        Initialize the SoftX theme GUI with the root window,
        and relevant helper class instances.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.theme_config = ["SoftX", "SoftX", "--background-image"]

        self.username = os.getlogin()
        self.css_file_path = None

        self.file_manager = FileManager(self.theme_config)
        self.backdrop_manager = BackdropManager(None)

        # Initialize base class template
        super().__init__(root, self.theme_config,
                         self.file_manager, self.backdrop_manager)

        self.setup = Setup
        self.setup.setup_gui(self, self.theme_config[0])
        self.setup_status_label()

        # Create a new frame for the image grid
        self.img_grid_frame = tk.Frame(self.root)
        self.img_grid_frame.pack(fill="both", expand=True)

        self.image_preview_instance = None

        self.root.title(
            f"VCTheme | {self.theme_config[0]} | {self.current_version}")

        self.setup_menu()

    def open_file(self):
        """
        Open a file dialog to select a CSS file.
        Overrides the base method to initialize the BackdropManager.
        """
        file_path = super().open_file()
        if file_path:
            self.css_file_path = file_path
            self.backdrop_manager = BackdropManager(self.css_file_path)
            with open(file_path, "r") as file:
                css_content = file.read()
                backdrop_urls = self.extract_backdrops(css_content)

            self.populate_dropdown(backdrop_urls)
