import tkinter as tk
from tkinter import messagebox
import re
import os
from setup import Setup
from backdrop_manager import BackdropManager
from file_manager import FileManager
from base_gui import BaseGUI

class SoftXGUI(BaseGUI):
    def __init__(self, root):
        # Theme configuration
        self.theme_config = ["SoftX", 0, "--background-image"]

        self.username = os.getlogin()
        self.css_file_path = f"C:\\Users\\{self.username}\\AppData\\Roaming\\Vencord\\themes\\SoftX.theme.css"

        # Initialize file and backdrop managers
        self.file_manager = FileManager(self.theme_config)
        self.backdrop_manager = BackdropManager(self.css_file_path)

        # Initialize base class template
        super().__init__(root, self.theme_config, self.file_manager, self.backdrop_manager)

        # Set up the GUI using the Setup class
        self.setup = Setup
        self.setup.setup_gui(self, self.theme_config[0])

        # Remove the existing text widget
        self.text.destroy()

        # Create a new frame for the image grid
        self.img_grid_frame = tk.Frame(self.root)
        self.img_grid_frame.pack(fill="both", expand=True)

        # Initialize image preview instance
        self.image_preview_instance = None
        self.root.title(f"VCTheme | {self.theme_config[0]} | {self.current_version}")

        # Set up the menu
        self.setup_menu()

    # Extract existing backdrops from file
    def extract_backdrops(self, css_text):
        backdrop_urls = []
        lines = css_text.split("\n")
        for line in lines:
            if self.theme_config[2] in line and "|" not in line:
                backdrop_url = line.split("url(")[1].split(")")[0]
                if backdrop_url not in backdrop_urls:
                    backdrop_urls.append(backdrop_url)
        return backdrop_urls

    # Add a new backdrop URL to the CSS file
    def add_backdrop_to_css(self):
        link = self.backdrop_entry.get()
        if link and re.match(r'^https?:\/\/.*\.(png|jpg|jpeg|gif)$', link):
            with open(self.css_file_path, "r") as file:
                css_content = file.readlines()

            # Check if the link is already present in the file
            if any(f"url({link})" in line for line in css_content):
                messagebox.showerror("Error", "This link is already present in the list of backdrops.")
                return

            # Find the index where the new backdrop should be added
            backdrop_index = -1
            for i, line in enumerate(css_content):
                if self.theme_config[2] in line and "url(" in line:
                    backdrop_index = i
                # bg blur comment fencepost fix
                elif line.strip().startswith("--background-blur"):
                    break

            with open(self.css_file_path, "w") as file:
                for i, line in enumerate(css_content):
                    file.write(line)
                    if i == backdrop_index:
                        file.write(f"/*{self.theme_config[2]}: url({link});*/\n")

            self.backdrop_menu['menu'].add_command(label=link, command=lambda u=link: self.set_active_backdrop(u))
            self.backdrop_entry.delete(0, tk.END)
            self.update_image_previews()
        else:
            messagebox.showerror("Error", "Please enter a valid URL with a .png, .jpg/jpeg, or .gif extension.")