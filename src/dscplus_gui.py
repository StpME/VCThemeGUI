import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os

def open_file():
    init_dir = os.path.join(os.environ['APPDATA'], 'Vencord', 'themes')
    file_path = filedialog.askopenfilename(initialdir=init_dir, filetypes=[("CSS files", "*.css")])
    if file_path:
        with open(file_path, "r") as file:
            css_content = file.read()
            text.delete(1.0, tk.END)  # Clear any existing text
            text.insert(tk.END, css_content)
            backdrop_urls_dark, backdrop_urls_light = extract_backdrops(css_content)
            populate_dropdown(backdrop_urls_dark + backdrop_urls_light)

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

# Make sure css file name and path is accurate
username = os.getlogin()
# css_file_path = f"C:\\Users\\{username}\\AppData\\Roaming\\Vencord\\themes\\DiscordPlus.theme.css"
css_file_path = f"C:\\Users\\{username}\\Documents\\Projects\\vencordThemeGUI\\src\\test.css"
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
            backdrop_entry.delete(0, tk.END)  # Clear the entry after adding the link
        else:
            # Display error message if the link is a duplicate
            messagebox.showerror("Error", "This link is already present in the list of backdrops.")
    else:
        # Display error message if the link is invalid
        messagebox.showerror("Error", "Please enter a valid URL with a .png, .jpg, or .jpeg extension.")

# Checks line to see if it is already commented out so comments arent appended
def is_backdrop_commented(line):
    return line.strip().startswith("/*") and line.strip().endswith("*/")

def update_css_file():
    if active_backdrop:
        with open(css_file_path, "r") as file:
            lines = file.readlines()

        with open(css_file_path, "w") as file:
            for line in lines:
                if "--dplus-backdrop" in line:
                    if active_backdrop in line:
                        if is_backdrop_commented(line):
                            file.write(line.replace("/*", "").replace("*/", ""))
                        else:
                            file.write(line)
                    elif not is_backdrop_commented(line):
                        file.write("/*" + line.strip() + "*/\n")
                    else:
                        file.write(line)
                else:
                    file.write(line)



# Main GUI window
root = tk.Tk()
root.title("CSS File Viewer")

label = tk.Label(root, text="Select Discord+ theme CSS file", font=("Arial", 12))
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
