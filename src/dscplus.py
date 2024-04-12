import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os
class DSCPlusGUI:
    # Grab user name to use for file path
    username = os.getlogin()
    # Default Vencord file path to css
    css_file_path = f"C:\\Users\\{username}\\AppData\\Roaming\\Vencord\\themes\\DiscordPlus.theme.css"
    # file path for testing locally
    # css_file_path = f"C:\\Users\\{username}\\AppData\\Roaming\\Vencord\\themes\\test.css"

    def __init__(self, root):
        self.root = root
        self.root.title("DSCPlus")
        
        self.setup_gui()
        self.setup_menu()
    
    def setup_gui(self):
        # GUI main headers
        self.label = tk.Label(self.root, text="Select Discord+ theme CSS file", font=("Arial", 12))
        self.label.pack()
        self.sub_label = tk.Label(self.root, text="Default Location: C:\\Users\\"+str(self.username)+"\\AppData\\Roaming\\Vencord\\themes", 
                            font=("Arial", 10))
        self.sub_label.pack()

        # Text shown for main window
        self.text = tk.Text(self.root, wrap="word")
        self.text.pack(expand=True, fill="both")
        
        # Dropdown menu
        self.backdrop_options = tk.StringVar(value="Select Backdrop")
        self.backdrop_menu = tk.OptionMenu(self.root, 
                                                self.backdrop_options,
                                                "Select Below"
                                            )
        self.backdrop_menu.pack(side=tk.LEFT,
                                    padx=5,
                                    pady=2,
                                    )

        self.backdrop_menu_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.backdrop_menu_label.pack(side=tk.LEFT)

        self.backdrop_entry = tk.Entry(self.root, width=50)
        self.backdrop_entry.pack(side=tk.RIGHT, padx=5, pady=5)

        # Add backdrop button
        self.add_backdrop_btn = tk.Button(self.root, text="Add Backdrop", 
                                        command=self.add_backdrop_to_css,
                                        bd=3 # Border width
                                    )
        self.add_backdrop_btn.pack(side=tk.RIGHT,
                                padx=5,
                                pady=5,
                            )
    # Toggle window stay on top
    def toggle_stay_on_top(self):
        self.root.attributes("-topmost", not self.root.attributes("-topmost"))

    # Create file menu for opening files and closing program
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_separator()
        filemenu.add_command(label="Stay on Top", command=self.toggle_stay_on_top)
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
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END,"Backdrop list:\n", "backdrop_label")
                self.text.tag_configure("backdrop_label", font=("Arial", 12, "bold"))
                self.text.insert(tk.END, DSCPlusGUI.get_unique_backdrops(self, css_content))
                backdrop_urls_dark, backdrop_urls_light = DSCPlusGUI.extract_backdrops(self, css_content)
                unique_backdrops = set(backdrop_urls_dark) | set(backdrop_urls_light)
                self.populate_dropdown(unique_backdrops)

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
    
    # Create set of unique backdrops from file
    def get_unique_backdrops(self, css_text):
        uniq_backdrops = set()
        for line in css_text.split("\n"):
            if "--dplus-backdrop" in line:
                uniq_backdrops.add(line.strip())
        return "\n".join(uniq_backdrops)

    # Fill in dropdown menu with extracted backdrops
    def populate_dropdown(self, backdrop_urls):
        self.backdrop_options.set("")
        uniq_urls = set()
        for url in backdrop_urls:
            if url not in uniq_urls:
                self.backdrop_menu['menu'].add_command(label=url, command=lambda u=url: self.set_active_backdrop(u))
                uniq_urls.add(url)

    # Set active backdrop based on the selected backdrop in dropdown
    def set_active_backdrop(self, selected_url):
        self.active_backdrop = selected_url
        self.backdrop_menu_label.config(text=selected_url)
        self.update_css_file()

        if self.text and os.path.exists(self.css_file_path):
            with open(self.css_file_path, "r") as file:
                css_content = file.read()
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, self.get_backdrop_section(css_content))

    # Find backdrop section within the theme section of the file
    def get_backdrop_section(self, css_content):
        dark_backdrops = set()
        current_section = None
        for line in css_content.split("\n"):
            if ".theme-dark" in line:
                current_section = "dark"
            elif "--dplus-backdrop" in line:
                if current_section == "dark":
                    dark_backdrops.add(line)
        return "Backdrop list:\n" + "\n".join(dark_backdrops)

    # Add the backdrop url to the file when button is clicked
    def add_backdrop_to_css(self):
        link = self.backdrop_entry.get()
        # Regex for valid link extension types
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

                with open(DSCPlusGUI.css_file_path, "w") as file:
                    for i, line in enumerate(css_content):
                        file.write(line)
                        if i == backdrop_section_dark:
                            file.write(f"/*--dplus-backdrop: url({link});*/\n")
                        elif i == backdrop_section_light:
                            file.write(f"/*--dplus-backdrop: url({link});*/\n")

                self.backdrop_menu['menu'].add_command(label=link, command=lambda u=link: self.set_active_backdrop(u))
                self.backdrop_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "This link is already present in the list of backdrops.")
        else:
            messagebox.showerror("Error", "Please enter a valid URL with a .png, .jpg/jpeg, or .gif extension.")

    # Check if backdrop is already commented to prevent appending additional comments
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