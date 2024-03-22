import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os

# ❌WIP: backdrop dropdown and main display list should be ordered the same way so its less confusing
def open_file():
    init_dir = os.path.join(os.environ['APPDATA'], 'Vencord', 'themes')
    file_path = filedialog.askopenfilename(initialdir=init_dir, filetypes=[("CSS files", "*.css")])
    if file_path:
        with open(file_path, "r") as file:
            css_content = file.read()
            text.delete(1.0, tk.END)  # Clear any existing text
            text.insert(tk.END, get_unique_backdrops(css_content)) # Get and display only unique lines
            backdrop_urls_dark, backdrop_urls_light = extract_backdrops(css_content)
            unique_backdrops = set(backdrop_urls_dark) | set(backdrop_urls_light)
            populate_dropdown(unique_backdrops) 

def get_unique_backdrops(css_text):
    uniq_backdrops = set()  # Set to track unique backdrop lines
    for line in css_text.split("\n"):
        if "--dplus-backdrop" in line:
            uniq_backdrops.add(line.strip())  # Add backdrop line to set
    return "\n".join(uniq_backdrops)

def extract_backdrops(css_text):
    backdrop_urls_dark = []
    backdrop_urls_light = []
    lines = css_text.split("\n")
    backdrop_section = None  # Parsing dark or light theme
    for line in lines:
        if ".theme-dark" in line:
            backdrop_section = "dark"
        elif ".theme-light" in line:
            backdrop_section = "light"
        elif "--dplus-backdrop" in line:
            # Extract url from within the text
            backdrop_url = line.split("url(")[1].split(")")[0]
            # Add to backdrop list
            if backdrop_section == "dark":
                backdrop_urls_dark.append(backdrop_url)
            elif backdrop_section == "light":
                backdrop_urls_light.append(backdrop_url)
    return backdrop_urls_dark, backdrop_urls_light

def populate_dropdown(backdrop_urls):
    backdrop_options.set("")
    # Set of urls so that dupes aren't displayed
    uniq_urls = set()
    for url in backdrop_urls:
        if url not in uniq_urls:
            backdrop_menu['menu'].add_command(label=url, command=lambda u=url: set_active_backdrop(u))
            uniq_urls.add(url)

def set_active_backdrop(selected_url):
    global active_backdrop
    active_backdrop = selected_url
    backdrop_menu_label.config(text=selected_url)
    update_css_file()

    # Reload the displayed CSS file content with the relevant section
    if text and os.path.exists(css_file_path):
        with open(css_file_path, "r") as file:
            css_content = file.read()
            text.delete(1.0, tk.END)  # Clear existing content
            text.insert(tk.END, get_backdrop_section(css_content))

def get_backdrop_section(css_content):
    dark_backdrops = []
    light_backdrops = []
    current_section = None
    # ❌WIP: need to figure out a simpler way to handle unique backdrops
    # Currently ignores light backdrops then only displays darks (since both share same backdrops)
    for line in css_content.split("\n"):
        if ".theme-dark" in line:
            current_section = "dark"
        elif ".theme-light" in line:
            current_section = "light"
        elif "--dplus-backdrop" in line:
            if current_section == "dark":
                dark_backdrops.append(line)
            elif current_section == "light":
                light_backdrops.append(line)
    return "Backdrop List:\n" + "\n".join(dark_backdrops)


# Make sure css file name and path is accurate
username = os.getlogin()

# Default Vencord file path to css
css_file_path = f"C:\\Users\\{username}\\AppData\\Roaming\\Vencord\\themes\\DiscordPlus.theme.css"
# file path for testing locally
# css_file_path = f"C:\\Users\\{username}\\Documents\\Projects\\vencordThemeGUI\\src\\test.css"

# ❌WIP: The main window should update the display when a backdrop is added
def add_backdrop_to_css():
    link = backdrop_entry.get()
    if link and re.match(r'^https?:\/\/.*\.(png|jpg|jpeg)$', link):
        with open(css_file_path, "r") as file:
            css_content = file.readlines()

        # Check if the link is already in the CSS file
        if not any(f"url({link})" in line for line in css_content):
            # Identify the last backdrop section for both dark and light themes
            backdrop_section_dark = -1
            backdrop_section_light = -1
            # Sets the dark and light themes to the index for each line
            for i, line in enumerate(css_content):
                if ".theme-dark" in line:
                    backdrop_section_dark = i
                elif ".theme-light" in line:
                    backdrop_section_light = i

            # Append the new backdrop link below the last backdrop in each section
            with open(css_file_path, "w") as file:
                for i, line in enumerate(css_content):
                    file.write(line)
                    if i == backdrop_section_dark:
                        file.write(f"/*--dplus-backdrop: url({link});*/\n")
                    elif i == backdrop_section_light:
                        file.write(f"/*--dplus-backdrop: url({link});*/\n")

            # Update the dropdown list with the new backdrop
            backdrop_menu['menu'].add_command(label=link, command=lambda u=link: set_active_backdrop(u))
            backdrop_entry.delete(0, tk.END)  # Clear the entry box after adding the link
        else:
            # Error for dupe links
            messagebox.showerror("Error", "This link is already present in the list of backdrops.")
    else:
        # Error for invalid links with wrong or missing extension
        messagebox.showerror("Error", "Please enter a valid URL with a .png, .jpg, or .jpeg extension.")

# Checks line to see if it is already commented out so comments arent appended
def is_backdrop_commented(line):
    return line.strip().startswith("/*") and line.strip().endswith("*/")

def update_css_file():
    if active_backdrop:
        with open(css_file_path, "r") as file:
            lines = file.readlines()

        with open(css_file_path, "w") as file:
            # unique_backdrops_dark = set()
            # unique_backdrops_light = set()
            for line in lines:
                # Handles the backdrop theme management
                if "--dplus-backdrop" in line:
                    # backdrop_url = line.split("(")[-1].split(")")[0]
                    # if backdrop_url not in unique_backdrops_dark and backdrop_url not in unique_backdrops_light:
                        if active_backdrop in line:
                            if is_backdrop_commented(line):
                                file.write(line.replace("/*", "").replace("*/", ""))
                            else:
                                file.write("/*" + line.strip() + "*/\n")
                        elif not is_backdrop_commented(line):
                            file.write("/*" + line.strip() + "*/\n")
                        else:
                            file.write(line)
                        # Add the url to both unique sets
                        # if ".theme-dark" in line:
                        #     unique_backdrops_dark.add(backdrop_url)
                        # elif ".theme-light" in line:
                        #     unique_backdrops_light.add(backdrop_url)
                # Writes rest of file
                else:
                    file.write(line)





# Main GUI window
root = tk.Tk()
root.title("DSCPlus")

label = tk.Label(root, text="Select Discord+ theme CSS file", font=("Arial", 12))
# Sub label to display the default file location of the file for the user
sub_label = tk.Label(root, text="Default Location: C:\\Users\\*USERNAME*\\AppData\\Roaming\\*MODDEDDISCORD*\\themes", 
                     font=("Arial", 10))
label.pack()
sub_label.pack()

# Display file contents
text = tk.Text(root, wrap="word")
text.pack(expand=True, fill="both")

# Create dropdown menu for backdrop selection
backdrop_label = tk.Label(root, text="Select Backdrop:", font=("Arial", 12))
backdrop_label.pack(side=tk.LEFT)

backdrop_options = tk.StringVar()
backdrop_menu = tk.OptionMenu(root, backdrop_options, "Select Below")
backdrop_menu.pack(side=tk.LEFT)

# Create label to display the selected backdrop
backdrop_menu_label = tk.Label(root, text="", font=("Arial", 12))
backdrop_menu_label.pack(side=tk.LEFT)

# Create entrybox and button for the user to input backdrop link and insert into dropdown
backdrop_entry = tk.Entry(root, width=50)
backdrop_entry.pack(side=tk.RIGHT, padx=5, pady=5)

add_button = tk.Button(root, text="Add Backdrop", command=add_backdrop_to_css)
add_button.pack(side=tk.RIGHT, padx=5, pady=5) 

# Create a menu bar to open directory for file and quit program
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=open_file)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)

# Run program
root.mainloop()
