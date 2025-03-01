import os
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

        # Get current version and set up the updater
        self.current_version = self.file_manager.get_version()
        self.repo = Setup.REPO
        self.exe_name = Setup.EXE_NAME
        self.updater = Updater(self.current_version, self.repo, self.exe_name)

        # Menu Github icon
        self.github_icon = None

        # Bind delete key for deleting selected backdrop
        self.root.bind("<Delete>", lambda event: self.delete_backdrop())

        # Track the last deleted backdrop URL and position
        self.last_deleted_url = None
        self.last_deleted_pos_list = []

        # Bind Ctrl+Z shortcut for restoring the last deleted backdrop
        self.root.bind("<Control-z>", lambda event: self.restore_last())

    def setup_menu(self):
        """
        Create the cascading file menu and it's components.
        """
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_separator()
        filemenu.add_command(label="Stay on Top", command=lambda:
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
        filemenu.add_command(label="Restore Last Deleted",
                             command=self.restore_last)
        filemenu.add_separator()
        filemenu.add_command(label="Check for Updates",
                             command=self.updater.check_for_updates)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",
                             command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def open_file(self):
        """
        Open and handle a CSS file, updating the GUI with its values.

        Returns:
            (string): The path to the opened file,
                      or None if no file was selected.
        """
        init_dir = os.path.join(os.environ['APPDATA'], 'Vencord', 'themes')
        file_path = filedialog.askopenfilename(
            initialdir=init_dir, filetypes=[("CSS files", "*.css")])
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

            # Read the CSS file and extract image URLs
            with open(file_path, "r"):
                css_content, img_urls = self.file_manager.extract_urls(
                    file_path)
                if css_content and img_urls:
                    # Create and store the ImagePreview instance
                    self.img_preview_instance = ImagePreview(
                        self.img_grid_frame, img_urls,
                        onclick=self.set_active_backdrop)

                    # Extract backdrops and populate the dropdown
                    backdrop_urls = self.extract_backdrops(css_content)

                    # Check for tuple backdrops in case of light + dark themes
                    if isinstance(backdrop_urls, tuple):
                        backdrop_urls = backdrop_urls[0] + backdrop_urls[1]

                    uniq_list = list(dict.fromkeys(backdrop_urls))
                    self.populate_dropdown(uniq_list)
            return file_path
        return None

    def populate_dropdown(self, backdrop_urls):
        """
        Populate the dropdown menu with extracted backdrop urls.

        Args:
            backdrop_urls (list): Backdrop urls to add to the dropdown menu.
        """
        self.backdrop_options.set("")
        uniq_urls = list()
        for url in backdrop_urls:
            if url not in uniq_urls:
                self.backdrop_menu['menu'].add_command(
                    label=url,
                    command=lambda u=url:
                    self.set_active_backdrop(u))
                uniq_urls.append(url)

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

    def delete_backdrop(self):
        """
        Delete the selected backdrop from the CSS file.
        """
        selected_url = self.active_backdrop

        if selected_url and selected_url != "Select Backdrop":
            confirm = messagebox.askyesno(
                "Delete Backdrop",
                f"Are you sure you want to delete '{selected_url}'?")
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
                    self.populate_dropdown(uniq_list)

                # Update the image previews
                self.update_image_previews()

                # Notify user of successful deletion
                messagebox.showinfo("Backdrop Deleted",
                                    f"'{selected_url}' has been deleted.")
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
