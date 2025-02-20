import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os
import webbrowser
from setup import Setup
from image_preview import ImagePreview
from PIL import Image, ImageTk

from updater import Updater
from backdrop_manager import BackdropManager
from file_manager import FileManager

class SoftXGUI:
    # Grab user name to use for file path
    username = os.getlogin()
    # Default Vencord file path to css
    css_file_path = f"C:\\Users\\{username}\\AppData\\Roaming\\Vencord\\themes\\SoftX.theme.css"

    def __init__(self, root):
        self.root = root
        # [0] = theme, [1] = ,[2] = backdrop string
        self.theme_config = ["SoftX", 0, "--background-image"]
        
        self.backdrop_manager = BackdropManager(self.css_file_path)
        self.file_manager = FileManager(self.theme_config)

        self.current_version = self.file_manager.get_version()
        self.repo = Setup.REPO
        self.exe_name = Setup.EXE_NAME
        
        self.updater = Updater(self.current_version, self.repo, self.exe_name)

        self.root.title(f"VCTheme | {self.theme_config[0]} | {self.current_version}")
        
        self.Setup = Setup
        self.Setup.setup_gui(self, self.theme_config[0])
        self.setup_menu()

        # Remove the existing text widget
        self.text.destroy() 

        # Create a new frame for the image grid
        self.img_grid_frame = tk.Frame(self.root)
        self.img_grid_frame.pack(fill="both", expand=True)

    # Create file menu for opening files and closing program
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_separator()
        filemenu.add_command(label="Stay on Top", command=lambda:Setup.toggle_stay_on_top(self.root))
        filemenu.add_separator()

        github_img = Image.open(self.file_manager.file_path("img/github_icon.png")).resize((16,16), Image.Resampling.LANCZOS)
        self.github_icon = ImageTk.PhotoImage(github_img)
        filemenu.add_command(label="Github", image=self.github_icon, compound=tk.RIGHT, command=self.Setup.open_github)

        filemenu.add_separator()
        filemenu.add_command(label="Check for Updates", command=self.updater.check_for_updates)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    # Open and handle CSS file, updating GUI with its values
    def open_file(self):
        init_dir = os.path.join(os.environ['APPDATA'], 'Vencord', 'themes')
        file_path = filedialog.askopenfilename(initialdir=init_dir, filetypes=[("CSS files", "*.css")])
        if file_path:
            self.backdrop_options = tk.StringVar(value="Select Backdrop")

            # Clear the existing image grid
            for widget in self.img_grid_frame.winfo_children():
                widget.destroy()

            # Clear the dropdown menu
            self.backdrop_menu['menu'].delete(0, 'end')
            self.backdrop_menu['menu'].add_command(label="Select Below")
            self.backdrop_menu['menu'].entryconfig(0, state="disabled") 
            self.backdrop_menu['menu'].add_separator()

            with open(file_path, "r") as file:
                css_content, img_urls = self.file_manager.extract_urls(file_path)
                if css_content and img_urls:
            
                    # Create and store the ImagePreview instance
                    self.img_preview_instance = ImagePreview(self.img_grid_frame, img_urls, onclick=self.set_active_backdrop)

                    backdrop_urls = self.extract_backdrops(css_content)
                    uniq_list = list(dict.fromkeys(backdrop_urls))
                    self.populate_dropdown(uniq_list)

    # Extract backdrops from file
    def extract_backdrops(self, css_text):
        backdrop_urls = []
        lines = css_text.split("\n")
        for line in lines:
            if self.theme_config[2] in line and "|" not in line:
                backdrop_url = line.split("url(")[1].split(")")[0]
                if backdrop_url not in backdrop_urls:
                    backdrop_urls.append(backdrop_url)
        return backdrop_urls

    # Fill in dropdown menu with extracted urls
    def populate_dropdown(self, backdrop_urls):
        self.backdrop_options.set("")
        uniq_urls = list()
        for url in backdrop_urls:
            if url not in uniq_urls:
                self.backdrop_menu['menu'].add_command(label=url, command=lambda u=url: self.set_active_backdrop(u))
                uniq_urls.append(url)

    # Set active backdrop based on the selected backdrop in dropdown
    def set_active_backdrop(self, selected_url):
        self.active_backdrop = selected_url
        self.backdrop_manager.update_css_file(self.active_backdrop, self.theme_config[2])

        # Highlight the selected image in the preview
        if self.img_preview_instance:
            self.img_preview_instance.highlight_image(selected_url)

    # Add the backdrop url to the file when button is clicked
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

  # Update the image previews when adding new backdrop
    def update_image_previews(self):
        if self.img_preview_instance:
            with open(self.css_file_path, "r") as file:
                css_content = file.read()
                img_urls = ImagePreview.extract_image_urls(css_content, self.theme_config[2])
                self.img_preview_instance.img_urls = img_urls
                self.img_preview_instance.load_images()