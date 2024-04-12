import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os
class SoftXGUI:
    # Grab user name to use for file path
    username = os.getlogin()
    # Default Vencord file path to css
    css_file_path = f"C:\\Users\\{username}\\AppData\\Roaming\\Vencord\\themes\\SoftX.theme.css"
    # file path for testing locally
    # css_file_path = f"C:\\Users\\{username}\\AppData\\Roaming\\Vencord\\themes\\test1.css"

    def __init__(self, root):
        self.root = root
        self.root.title("SoftX")
        
        self.setup_gui()
        self.setup_menu()
    
    def setup_gui(self):
        # GUI main headers
        self.label = tk.Label(self.root, text="Select SoftX theme CSS file", font=("Arial", 12))
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

                self.text.insert(tk.END, SoftXGUI.get_unique_backdrops(self, css_content))
                backdrop_urls = SoftXGUI.extract_backdrops(self, css_content)
                unique_backdrops = set(backdrop_urls)
                self.populate_dropdown(unique_backdrops)

    # Extract backdrops from file
    def extract_backdrops(self, css_text):
        backdrop_urls = []
        lines = css_text.split("\n")
        for line in lines:
            if "--background-image:" in line:
                url = self.get_clean_url(line)
                backdrop_urls.append(url)

                
        return backdrop_urls
    
    def get_clean_url(self, line):
        url = line.split("url(")[1].split(")")[0]
        # Ignore "" in the url for cleaner display
        if '"' in url:
            url = url.strip('"')
        return url
    
    # Create set of unique backdrops from file
    def get_unique_backdrops(self, css_text):
        uniq_backdrops = set()
        for line in css_text.split("\n"):
            if "--background-image:" in line:
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
        backdrops = set()
        for line in css_content.split("\n"):
            if "--background-image:" in line:
                backdrops.add(line)
        return "Backdrop list:\n" + "\n".join(backdrops)

    # Add the backdrop url to the file when button is clicked
    def add_backdrop_to_css(self):
        link = self.backdrop_entry.get()
        # Regex for valid url extension types that aren't empty
        if link and re.match(r'^https?:\/\/.*\.(png|jpg|jpeg|gif)$', link):
            with open(SoftXGUI.css_file_path, "r") as file:
                css_content = file.readlines()

            # Get index of the last backdrop
            index_last_backdrop = len(css_content) - 1
            for i, line in reversed(list(enumerate(css_content))):
                if "--background-image:" in line:
                    index_last_backdrop = i
                    break
            
            # Check if link is present in file
            if not any(f"url({link})" in line for line in css_content):
                with open(SoftXGUI.css_file_path, "w") as file:
                    # Write each line of the CSS content
                    for i, line in enumerate(css_content):
                        file.write(line)
                        # If at given last backdrop index, insert backdrop below it
                        if i == index_last_backdrop:
                            file.write(f"/*--background-image: url({link});*/\n")
                    
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
            with open(SoftXGUI.css_file_path, "r") as file:
                lines = file.readlines()

            with open(SoftXGUI.css_file_path, "w") as file:
                for line in lines:
                    # Split line at the semicolon and write only backdrop without initial file comments
                    if "Background image |" in line:
                        line = line.split(';')[0].strip() + ';\n'
                        line = line.strip("/*") # strip leading comment
                        file.write(line)
                    # Handle other backdrops normally
                    elif "--background-image:" in line:
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