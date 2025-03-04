import tkinter as tk
from tkinter import messagebox
import re
import os
from setup import Setup
from backdrop_manager import BackdropManager
from file_manager import FileManager
from base_gui import BaseGUI


class ClearVisGUI(BaseGUI):
    """
    Theme specific class for individual syntax not managed by the base gui.
    Includes methods for extracting and adding backdrops to the CSS file.
    Inherits from the BaseGUI class.
    """
    def __init__(self, root):
        """
        Initialize the ClearVision theme GUI with the root window,
        and relevant helper class instances.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.theme_config = ["ClearVision", "ClearVision",
                             "--background-image"]

        self.username = os.getlogin()
        self.css_file_path = None

        self.file_manager = FileManager(self.theme_config)
        self.backdrop_manager = BackdropManager(None)

        # Initialize base class template
        super().__init__(root, self.theme_config,
                         self.file_manager, self.backdrop_manager)

        self.setup = Setup
        self.setup.setup_gui(self, self.theme_config[0])

        # Remove any existing text widget
        self.text.destroy()

        # Create a new frame for the image grid
        self.img_grid_frame = tk.Frame(self.root)
        self.img_grid_frame.pack(fill="both", expand=True)

        self.image_preview_instance = None

        self.root.title(
            f"VCTheme | {self.theme_config[0]} | {self.current_version}")

        self.setup_menu()

    def extract_backdrops(self, css_text):
        """
        Extract existing backdrop urls from the CSS file.

        Args:
            css_text (string): The CSS file content.
        """
        backdrop_urls = []
        lines = css_text.split("\n")
        for line in lines:
            if self.theme_config[2] in line and "url(" in line:
                url_start = line.find("url(") + 4  # Start after url(
                url_end = line.find(")", url_start)  # Find closing )
                backdrop_url = line[url_start:url_end].strip()

                # Add the URL to the list if it's not already there
                if backdrop_url and backdrop_url not in backdrop_urls:
                    backdrop_urls.append(backdrop_url)
        return backdrop_urls

    def open_file(self):
        """
        Open a file dialog to select a CSS file.
        Overrides the base method to initialize the BackdropManager.
        """
        file_path = super().open_file()
        if file_path:
            self.css_file_path = file_path
            self.backdrop_manager = BackdropManager(self.css_file_path)

    def add_backdrop_to_css(self):
        """
        Add a new backdrop url to the CSS file.
        Includes checks for loaded file, duplicates and valid url formats.
        """
        # Check if a file has been loaded
        if (self.css_file_path is None or
                not os.path.exists(self.css_file_path)):
            messagebox.showerror(
                "Error",
                "Please load a CSS file before adding a backdrop.")
            return
        link = self.backdrop_entry.get()
        if link and re.match(r'^https?:\/\/.*\.(png|jpg|jpeg|gif)$', link):
            with open(self.css_file_path, "r") as file:
                css_content = file.readlines()

            # Check if the link is already present in the file
            if any(f"url({link})" in line for line in css_content):
                messagebox.showerror(
                    "Error",
                    "This link is already present in the list of backdrops.")
                return

            # Find the index where the new backdrop should be added
            backdrop_index = -1
            for i, line in enumerate(css_content):
                if self.theme_config[2] in line and "url(" in line:
                    backdrop_index = i

            with open(self.css_file_path, "w") as file:
                for i, line in enumerate(css_content):
                    file.write(line)
                    if i == backdrop_index:
                        file.write(
                            f"/*{self.theme_config[2]}: url({link});*/\n")

            self.backdrop_menu['menu'].add_command(
                label=link,
                command=lambda u=link: self.set_active_backdrop(u))
            self.backdrop_entry.delete(0, tk.END)
            self.update_image_previews()
        else:  # Check if given valid url format
            messagebox.showerror(
                "Error",
                "Please enter a valid URL with a "
                ".png, .jpg/jpeg, or .gif extension.")
