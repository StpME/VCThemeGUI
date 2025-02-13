import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os
import webbrowser
from setup import Setup
from img_preview import ImagePreview
from PIL import Image, ImageTk

class DSCPlusGUI:
    # Grab user name to use for file path
    username = os.getlogin()
    # Default Vencord file path to css
    css_file_path = f"C:\\Users\\{username}\\AppData\\Roaming\\Vencord\\themes\\DiscordPlus.theme.css"

    def __init__(self, root):
        self.root = root
        self.root.title("VCTheme - DSCPlus")
        self.Setup = Setup
        self.Setup.setup_gui(self, "Discord+")
        self.setup_menu()

        # Remove the existing text widget
        self.text.destroy() 

        # Create a new frame for the image grid
        self.img_grid_frame = tk.Frame(self.root)
        self.img_grid_frame.pack(fill="both", expand=True)

        # Initialize the ImagePreview instance as None
        self.image_preview_instance = None

    # Toggle window stay on top
    def toggle_stay_on_top(self):
        self.root.attributes("-topmost", not self.root.attributes("-topmost"))

    # Link to project Github page
    def open_github(self):
        webbrowser.open_new("https://github.com/StpME/VCThemeGUI")


    # Create file menu for opening files and closing program
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_separator()
        filemenu.add_command(label="Stay on Top", command=self.toggle_stay_on_top)
        filemenu.add_separator()

        github_img = Image.open("src/img/github_icon.png").resize((16,16), Image.Resampling.LANCZOS)
        self.github_icon = ImageTk.PhotoImage(github_img)
        filemenu.add_command(label="Github", image=self.github_icon, compound=tk.RIGHT, command=self.open_github)
        
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
            with open(file_path, "r") as file:
                css_content = file.read()
                # Extract image URLs from the CSS
                img_urls = ImagePreview.extract_img_urls(css_content)
                
                # Clear the existing image grid
                for widget in self.img_grid_frame.winfo_children():
                    widget.destroy()
                
                # Create and store the ImagePreview instance
                self.image_preview_instance = ImagePreview(self.img_grid_frame, img_urls)

                backdrop_urls_dark, backdrop_urls_light = self.extract_backdrops(css_content)
                combined_backdrops = backdrop_urls_dark + backdrop_urls_light
                unique_list = list(dict.fromkeys(combined_backdrops))
                self.populate_dropdown(unique_list)

    # Extract backdrops from file
    def extract_backdrops(self, css_text):
        backdrop_urls_dark = []
        backdrop_urls_light = []
        lines = css_text.split("\n")
        backdrop_section = None
        for line in lines:
            if ".theme-dark" in line:
                backdrop_section = "dark"
            elif ".theme-light" in line:
                backdrop_section = "light"
            elif "--dplus-backdrop" in line:
                backdrop_url = line.split("url(")[1].split(")")[0]
                if backdrop_section == "dark":
                    backdrop_urls_dark.append(backdrop_url)
                elif backdrop_section == "light":
                    backdrop_urls_light.append(backdrop_url)
        return backdrop_urls_dark, backdrop_urls_light
    
    # Create list of unique backdrops directly from file
    def get_unique_backdrops(self, css_text):
        uniq_backdrops = list()
        for line in css_text.split("\n"):
            backdrop = line.strip()
            if "--dplus-backdrop" in line and backdrop not in uniq_backdrops:
                uniq_backdrops.append(backdrop)
        return "\n".join(uniq_backdrops)

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
        # self.backdrop_menu_label.config(text=selected_url)
        self.update_css_file()

        if self.text and os.path.exists(self.css_file_path):
            with open(self.css_file_path, "r") as file:
                css_content = file.read()
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, self.get_backdrop_section(css_content))

    # Find backdrop section within the theme section of the file (only checks dark theme)
    def get_backdrop_section(self, css_content):
        dark_backdrops = list()
        current_section = None
        for line in css_content.split("\n"):
            if ".theme-dark" in line:
                current_section = "dark"
            elif "--dplus-backdrop" in line:
                if current_section == "dark" and line not in dark_backdrops:
                    dark_backdrops.append(line)
        return "Backdrop list:\n" + "\n".join(dark_backdrops)

    # Add the backdrop url to the file when button is clicked
    def add_backdrop_to_css(self):
        link = self.backdrop_entry.get()
        if link and re.match(r'^https?:\/\/.*\.(png|jpg|jpeg|gif)$', link):
            with open(DSCPlusGUI.css_file_path, "r") as file:
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
                    if "--dplus-backdrop" in line and i > backdrop_section_dark and (backdrop_section_light == -1 or i < backdrop_section_light):
                        index_last_backdrop_dark = i
                        break

                for i, line in reversed(list(enumerate(css_content))):
                    if "--dplus-backdrop" in line and i > backdrop_section_light:
                        index_last_backdrop_light = i
                        break

                with open(DSCPlusGUI.css_file_path, "w") as file:
                    for i, line in enumerate(css_content):
                        file.write(line)
                        if i == index_last_backdrop_dark and backdrop_section_dark != -1:
                            file.write(f"/*--dplus-backdrop: url({link});*/\n")
                        if i == index_last_backdrop_light and backdrop_section_light != -1:
                            file.write(f"/*--dplus-backdrop: url({link});*/\n")

                self.backdrop_menu['menu'].add_command(label=link, command=lambda u=link: self.set_active_backdrop(u))
                self.backdrop_entry.delete(0, tk.END)
                self.update_image_previews()
            else:
                messagebox.showerror("Error", "This link is already present in the list of backdrops.")
        else:
            messagebox.showerror("Error", "Please enter a valid URL with a .png, .jpg/jpeg, or .gif extension.")

    # Check if backdrop is already commented out to prevent appending additional comments
    def is_backdrop_commented(self, line):
        return line.strip().startswith("/*") and line.strip().endswith("*/")

    # Update file with active backdrop
    def update_css_file(self):
        if self.active_backdrop:
            with open(DSCPlusGUI.css_file_path, "r") as file:
                lines = file.readlines()

            with open(DSCPlusGUI.css_file_path, "w") as file:
                for line in lines:
                    if "--dplus-backdrop" in line:
                        if self.active_backdrop in line:
                            if self.is_backdrop_commented(line):
                                file.write(line.replace("/*", "").replace("*/", ""))
                            else:
                                file.write("/*" + line.strip() + "*/\n")
                        elif not self.is_backdrop_commented(line):
                            file.write("/*" + line.strip() + "*/\n")
                        else:
                            file.write(line)
                    else:
                        file.write(line)
            # self.update_image_previews()

    # Update the image previews when adding new backdrop
    def update_image_previews(self):
        if self.image_preview_instance:
            with open(self.css_file_path, "r") as file:
                css_content = file.read()
                img_urls = ImagePreview.extract_img_urls(css_content)
                self.image_preview_instance.img_urls = img_urls
                self.image_preview_instance.load_imgs()
