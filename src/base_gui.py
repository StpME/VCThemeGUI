import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from image_preview import ImagePreview
from PIL import Image, ImageTk
from setup import Setup
from updater import Updater


class BaseGUI:
    """
    Base class for managing the GUI, for extension by theme-specific classes.
    Includes file operations, backdrop management, and UI setup
    """
    def __init__(self, root, theme_config, file_manager, backdrop_manager):
        """
        Initialize the BaseGUI with the root window, theme configuration,
        with the file and backdrop managers.

        Args:
            root (tk.Tk): The root Tkinter window.
            theme_config (list): Contains theme specific configuration details.
            file_manager (FileManager): An instance of the FileManager class.
            backdrop_manager (BackdropManager): An instance of the
                                                BackdropManager class.
        """
        self.root = root
        self.theme_config = theme_config
        self.file_manager = file_manager
        self.backdrop_manager = backdrop_manager

        # GUI components
        self.img_grid_frame = None
        self.img_preview_instance = None
        self.backdrop_menu = None
        self.backdrop_options = None
        self.backdrop_entry = None
        self.add_backdrop_btn = None
        self.active_backdrop = None
        self.header_label = None

        # Get current version and set up the updater
        self.current_version = self.file_manager.get_version()
        self.repo = Setup.REPO
        self.exe_name = Setup.EXE_NAME
        self.updater = Updater(self.current_version, self.repo,
                               self.exe_name, self.root)

        # Menu Github icon
        self.github_icon = None

        # Bind delete key for deleting selected backdrop
        self.root.bind("<Delete>", lambda event: self.delete_backdrop())

        # Track the last deleted backdrop URL and position
        self.last_deleted_url = None
        self.last_deleted_pos_list = []

        # Bind Ctrl+Z shortcut for restoring the last deleted backdrop
        self.root.bind("<Control-z>", lambda event: self.restore_last())
        # Bind Ctrl+T shortcut for anchoring window on top
        self.root.bind("<Control-t>",
                       lambda event: Setup.toggle_stay_on_top(self.root))
        # Bind Enter shortcut for adding backdrop
        self.root.bind("<Return>",
                       lambda event: self.add_backdrop_to_css())

    def setup_menu(self):
        """
        Create the cascading file menu and it's components.
        """
        menubar = tk.Menu(self.root)

        # File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_separator()
        filemenu.add_command(label="Stay on Top (Ctrl+T)", command=lambda:
                             Setup.toggle_stay_on_top(self.root))
        filemenu.add_separator()
        github_img = Image.open(self.file_manager
                                .file_path("img/github_icon.png")).resize(
                                    (16, 16), Image.Resampling.LANCZOS)
        self.github_icon = ImageTk.PhotoImage(github_img)
        filemenu.add_command(label="Github", image=self.github_icon,
                             compound=tk.RIGHT,
                             command=Setup.open_github)
        filemenu.add_separator()
        filemenu.add_command(label="Check for Updates",
                             command=self.updater.check_for_updates)
        filemenu.add_separator()
        filemenu.add_command(label="Select Different GUI",
                             command=self.return_to_selector)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",
                             command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # Edit menu
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Restore Last Deleted (Ctrl+Z)",
                             command=self.restore_last)
        editmenu.add_separator()
        editmenu.add_command(label="Delete Selected (Del)",
                             command=self.delete_backdrop)
        menubar.add_cascade(label="Edit", menu=editmenu)
        self.root.config(menu=menubar)

    def is_valid_css_file(self, file_path):
        """
        Check if the CSS file name contains the expected theme alias.

        Args:
            file_path (string): The path to the CSS file.

        Returns:
            (boolean): True if the file name matches the expected theme,
            False if not.
        """
        file_name = os.path.basename(file_path).lower()
        theme_name = self.theme_config[0].lower()
        theme_alias = self.theme_config[1].lower()
        return theme_name in file_name or theme_alias in file_name

    def open_file(self):
        """
        Open and handle a CSS file, updating the GUI with its values.

        Returns:
            (string): The path to the opened file,
                      or None if no file was selected.
        """
        while True:
            init_dir = os.path.join(os.environ['APPDATA'], 'Vencord', 'themes')
            file_path = filedialog.askopenfilename(
                initialdir=init_dir, filetypes=[("CSS files", "*.css")])
            if not file_path:  # user cancels file dialog
                return None

            if not self.is_valid_css_file(file_path):
                # display warning & ask user if they want to continue
                warning_message = (
                    f"The selected file does not match the expected theme.\n\n"
                    f"Expected: {self.theme_config[1]} in the file name.\n"
                    f"Selected file: {os.path.basename(file_path)}\n\n"
                    "Do you want to select a different file?"
                )
                if messagebox.askyesno("Warning: Incorrect CSS File",
                                       warning_message):
                    # recursive call to select diff file
                    return self.open_file()
                else:  # user chose to use current file
                    break
            else:  # file was already valid
                break

        self.backdrop_options = tk.StringVar(value="Select Backdrop")

        # Clear the existing image grid
        for widget in self.img_grid_frame.winfo_children():
            widget.destroy()

        # Clear the dropdown menu
        self.backdrop_menu['menu'].delete(0, 'end')
        self.backdrop_menu['menu'].add_command(label="Select Below")
        self.backdrop_menu['menu'].entryconfig(0, state="disabled")
        self.backdrop_menu['menu'].add_separator()

        # Read the CSS file and extract image URLs
        with open(file_path, "r"):
            css_content, img_urls = self.file_manager.extract_urls(file_path)
            if css_content and img_urls:

                # Extract backdrops and populate the dropdown
                backdrop_urls = self.extract_backdrops(css_content)

                # Update label when a file is loaded
                self.header_label.config(
                    text="Select a backdrop by clicking on an image"
                         " or using 'Select Backdrop'",
                    font=("Arial", 12, "bold")
                )
                self.sub_label.config(
                    text=f"Loaded {len(backdrop_urls)} backdrops from: "
                    f"{os.path.basename(file_path)}",
                    font=("Arial", 9)
                )
                self.sub_label.pack()

                # Create and store the ImagePreview instance
                self.img_preview_instance = ImagePreview(
                    self.img_grid_frame, img_urls,
                    onclick=self.set_active_backdrop)

                # Check for tuple backdrops in case of light + dark themes
                if isinstance(backdrop_urls, tuple):
                    backdrop_urls = backdrop_urls[0] + backdrop_urls[1]

                uniq_list = list(dict.fromkeys(backdrop_urls))
                self.populate_dropdown(uniq_list)

        return file_path

    def extract_backdrops(self, css_text):
        """
        Extract existing backdrop urls from the CSS file.
        Preserves the order of urls and avoids duplicates.

        Args:
            css_text (string): The CSS file content.

        Returns:
            list: A list of backdrop urls in descending order from CSS file.
        """
        backdrop_urls = []
        lines = css_text.split("\n")
        for line in lines:
            # Check if the line contains the backdrop property and a URL
            if self.theme_config[2] in line and "url(" in line:
                # Extract the URL from the line
                url_start = line.find("url(") + 4  # After "url(" for img url
                url_end = line.find(")", url_start)  # Find the closing ")"
                backdrop_url = line[url_start:url_end].strip()

                # Remove any quotes around the URL
                if backdrop_url.startswith('"') and backdrop_url.endswith('"'):
                    backdrop_url = backdrop_url[1:-1]
                elif (backdrop_url.startswith("'") and
                      backdrop_url.endswith("'")):
                    backdrop_url = backdrop_url[1:-1]

                # Add the URL to the list if unique
                if backdrop_url and backdrop_url not in backdrop_urls:
                    backdrop_urls.append(backdrop_url)
        return backdrop_urls

    def populate_dropdown(self, backdrop_urls):
        """
        Populate the dropdown menu with extracted backdrop urls.

        Args:
            backdrop_urls (list): Backdrop urls to add to the dropdown menu.
        """
        # Reset the dropdown except descriptor and separator
        menu = self.backdrop_menu['menu']
        menu.delete(2, 'end')

        for url in backdrop_urls:
            count = menu.index('end')
            menu.add_command(
                label=f"({count}) {url}",
                command=lambda u=url: self.set_active_backdrop(u)
            )

    def set_active_backdrop(self, selected_url):
        """
        Set active backdrop based on the selected backdrop

        Args:
            selected_url (string): The url of the selected backdrop.
        """
        self.active_backdrop = selected_url
        self.backdrop_manager.update_css_file(self.active_backdrop,
                                              self.theme_config[2])

        # Highlight the selected image in the preview
        if self.img_preview_instance:
            self.img_preview_instance.highlight_image(selected_url)

    def add_backdrop_to_css(self):
        """
        Add a new backdrop URL to the CSS file.
        Handles themes with a single backdrop property.
        Includes checks for loaded file, duplicates and valid url formats.

        Args:
            link (string): The backdrop URL to add.
        """
        link = self.backdrop_entry.get()
        # Check if a file has been loaded
        if not self.css_file_path or not os.path.exists(self.css_file_path):
            messagebox.showerror(
                "Error",
                "Please load a CSS file before adding a backdrop.")
            return

        # Validate url format
        if not link or not re.match(r'^https?:\/\/.*\.(png|jpg|jpeg|gif)$',
                                    link):
            messagebox.showerror(
                "Error",
                "Please enter a valid URL with a .png, "
                ".jpg/jpeg, or .gif extension.")
            return

        # Read the CSS file
        with open(self.css_file_path, "r") as file:
            css_content = file.readlines()

        # Check for duplicate links
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

        # Write the updated CSS file
        with open(self.css_file_path, "w") as file:
            for i, line in enumerate(css_content):
                file.write(line)
                if i == backdrop_index:
                    file.write(f"/*{self.theme_config[2]}: url({link});*/\n")

        # Update sub label with the new link added
        self.sub_label.config(
                text=f"Added ({link}) to list of backdrops",
                font=("Arial", 9)
            )
        self.sub_label.pack()

        # Update the dropdown & image previews
        menu = self.backdrop_menu['menu']
        count = menu.index("end")

        menu.add_command(
            label=f"({count}) {link}",
            command=lambda u=link: self.set_active_backdrop(u)
        )
        self.backdrop_entry.delete(0, tk.END)
        self.update_image_previews()

    def delete_backdrop(self):
        """
        Delete the selected backdrop from the CSS file.
        Prevents deletion of last backdrop in file.
        """
        selected_url = self.active_backdrop

        if selected_url and selected_url != "Select Backdrop":

            with open(self.css_file_path, "r") as file:
                css_content = file.read()
                backdrop_urls = self.extract_backdrops(css_content)
            if len(backdrop_urls) == 1:
                confirm = messagebox.showinfo(
                 "Can't Delete Backdrop",
                 "You can't delete the last backdrop in the CSS file."
                )
                return
            confirm = messagebox.askyesno(
                "Delete Backdrop",
                f"Are you sure you want to delete '{selected_url}'?"
            )
            if confirm:
                # Read the CSS file
                with open(self.css_file_path, "r") as file:
                    lines = file.readlines()

                # Track positions of the selected URL for both light and dark
                self.last_deleted_url = selected_url
                self.last_deleted_pos_list = []

                for i, line in enumerate(lines):
                    if f"url({selected_url})" in line:
                        self.last_deleted_pos_list.append(i)

                # Rewrite the CSS file without the line(s) of the selected URL
                with open(self.css_file_path, "w") as file:
                    for line in lines:
                        if f"url({selected_url})" not in line:
                            file.write(line)

                # Remove the backdrop from the dropdown menu
                self.backdrop_menu['menu'].delete(0, 'end')
                self.backdrop_menu['menu'].add_command(label="Select Below",
                                                       state="disabled")
                self.backdrop_menu['menu'].add_separator()

                # Re-extract and populate the dropdown with updated backdrops
                with open(self.css_file_path, "r") as file:
                    css_content = file.read()
                    backdrop_urls = self.extract_backdrops(css_content)
                    if isinstance(backdrop_urls, tuple):  # Handle l+d themes
                        backdrop_urls = backdrop_urls[0] + backdrop_urls[1]
                    uniq_list = list(dict.fromkeys(backdrop_urls))
                    self.set_active_backdrop(uniq_list[0])
                    self.populate_dropdown(uniq_list)

                # Update the image previews
                self.update_image_previews()

                # Notify user of successful deletion
                messagebox.showinfo("Backdrop Deleted",
                                    f"'{selected_url}' has been deleted.")

                # Update sub label with deleted link notice
                self.sub_label.config(
                        text=f"Deleted ({selected_url}) from "
                        "list of backdrops",
                        font=("Arial", 9)
                    )
                self.sub_label.pack()

        else:  # Notify user if no backdrop is currently selected to delete
            messagebox.showwarning("No Backdrop Selected",
                                   "Please select a backdrop to delete.")

    def restore_last(self):
        """
        Restores the last deleted backdrop URL to the CSS file then
        re-populates the dropdown and image previews with restored backdrop.
        """
        if self.last_deleted_url and self.last_deleted_pos_list:
            # Read the CSS file
            with open(self.css_file_path, "r") as file:
                lines = file.readlines()

            # Insert the last deleted URL at its original position(s)
            for pos in self.last_deleted_pos_list:
                restored_line = (
                    f"/*{self.theme_config[2]}: url("
                    f"{self.last_deleted_url});*/\n"
                )

                # Check if the position is within the bounds of the file
                if 0 <= pos < len(lines):
                    # Insert the restored line without adding extra blank lines
                    lines.insert(pos, restored_line)

            # Write the updated CSS file
            with open(self.css_file_path, "w") as file:
                file.writelines(lines)

            # Re-extract and populate the dropdown with updated backdrops
            with open(self.css_file_path, "r") as file:
                css_content = file.read()
                backdrop_urls = self.extract_backdrops(css_content)
                if isinstance(backdrop_urls, tuple):  # Handle l+d themes
                    backdrop_urls = backdrop_urls[0] + backdrop_urls[1]
                uniq_list = list(dict.fromkeys(backdrop_urls))
                self.populate_dropdown(uniq_list)

            # Update the image previews
            self.update_image_previews()

            # Set the restored backdrop to active again so active isn't empty
            self.set_active_backdrop(self.last_deleted_url)

            # Update sub label with deleted link notice
            self.sub_label.config(
                    text=f"Restored ({self.last_deleted_url}) to "
                    "list of backdrops",
                    font=("Arial", 9)
                )
            self.sub_label.pack()

            # Notify user of successful restoration
            messagebox.showinfo(
                "Backdrop Restored",
                f"'{self.last_deleted_url}' has been restored.")

            # Reset the last deleted URL and positions
            self.last_deleted_url = None
            self.last_deleted_pos_list = None
        else:
            messagebox.showwarning(
                "No Backdrop to Restore",
                "No backdrop has been deleted recently.")

    def update_image_previews(self):
        """
        Update the image previews when new backdrop url is detected.
        """
        if self.img_preview_instance:
            with open(self.css_file_path, "r") as file:
                css_content = file.read()
                img_urls = ImagePreview.extract_image_urls(
                    css_content,
                    self.theme_config[2])
                self.img_preview_instance.img_urls = img_urls
                self.img_preview_instance.load_images()

    def cleanup(self):
        """
        Reset common variables and resources.
        Used for if user wants to return to the GUI selector.
        """
        self.css_file_path = None
        self.backdrop_manager = None
        self.image_preview_instance = None
        self.active_backdrop = None
        self.last_deleted_url = None
        self.last_deleted_pos_list = []
        self.backdrop_options = None

    def return_to_selector(self):
        """
        Destroy the current GUI and return to the GUI selector.
        """
        self.cleanup()
        self.root.destroy()
        from main import main
        main()
