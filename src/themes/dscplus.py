import tkinter as tk
from tkinter import messagebox
import re
import os
from setup import Setup
from backdrop_manager import BackdropManager
from file_manager import FileManager
from base_gui import BaseGUI


class DSCPlusGUI(BaseGUI):
    """
    Theme specific class for individual syntax not managed by the base gui.
    Includes methods for extracting and adding backdrops to the CSS file.
    Inherits from the BaseGUI class.
    """
    def __init__(self, root):
        """
        Initialize the Discord+ theme GUI with the root window,
        and relevant helper class instances.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.theme_config = ["Discord+", "DiscordPlus", "--dplus-backdrop"]

        self.username = os.getlogin()
        self.css_file_path = None

        self.file_manager = FileManager(self.theme_config)
        self.backdrop_manager = BackdropManager(None)

        # Initialize base class template
        super().__init__(root, self.theme_config,
                         self.file_manager, self.backdrop_manager)

        self.setup = Setup
        self.setup.setup_gui(self, self.theme_config[0])

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

            if not any(f"url({link})" in line for line in css_content):
                backdrop_section_dark = -1
                backdrop_section_light = -1
                for i, line in enumerate(css_content):
                    if ".theme-dark" in line:
                        backdrop_section_dark = i
                    elif ".theme-light" in line:
                        backdrop_section_light = i

                index_last_backdrop_dark = -1
                index_last_backdrop_light = -1
                for i, line in reversed(list(enumerate(css_content))):
                    if (self.theme_config[2] in line and
                            i > backdrop_section_dark and
                            (backdrop_section_light == -1 or
                             i < backdrop_section_light)):
                        index_last_backdrop_dark = i
                        break

                for i, line in reversed(list(enumerate(css_content))):
                    if (self.theme_config[2] in line and
                            i > backdrop_section_light):
                        index_last_backdrop_light = i
                        break

                with open(self.css_file_path, "w") as file:
                    for i, line in enumerate(css_content):
                        file.write(line)
                        if (i == index_last_backdrop_dark and
                                backdrop_section_dark != -1):
                            file.write(
                                f"/*{self.theme_config[2]}: url({link});*/\n")
                        if (i == index_last_backdrop_light and
                                backdrop_section_light != -1):
                            file.write(
                                f"/*{self.theme_config[2]}: url({link});*/\n")

                self.backdrop_menu['menu'].add_command(
                    label=link,
                    command=lambda u=link: self.set_active_backdrop(u))
                self.backdrop_entry.delete(0, tk.END)
                self.update_image_previews()
            else:  # Check if the link is already present in the file
                messagebox.showerror(
                    "Error",
                    "This link is already present in the list of backdrops.")
        else:  # Check if given valid url format
            messagebox.showerror(
                "Error",
                "Please enter a valid URL with a "
                ".png, .jpg/jpeg, or .gif extension.")
