import tkinter as tk
import webbrowser


class Setup:
    """
    Handles the setup and configuration of the GUI,
    including program layout and event key bindings.
    """
    REPO = "StpME/VCThemeGUI"
    EXE_NAME = "VCTheme"

    def setup_gui(self, gui_name):
        """
        Set up the GUI layout and components.

        Args:
            gui_name (string): The name of the GUI theme being set up.
        """
        # Create an dark border for top/btm and remove left + right edges
        border_top_frame = tk.Frame(self.root, bg="gray")
        border_top_frame.pack(fill="x")

        border_btm_frame = tk.Frame(self.root, bg="gray")
        border_btm_frame.pack(side="bottom", fill="x")

        # Create header label frame
        label_frame = tk.Frame(border_top_frame, bg="lightgray")
        label_frame.pack(fill="x", pady=2)

        # Backdrop frame for button and entry box
        btm_frame = tk.Frame(border_btm_frame, bg="lightgray")
        btm_frame.pack(side="bottom", fill="x", pady=2)

        self.header_label = tk.Label(
            label_frame,
            text=f"Select {gui_name} theme from File menu",
            font=("Arial", 12, "bold"),
            bg="lightgray"
        )
        # Initialize sub label, is only packed in GUI on file load
        self.sub_label = tk.Label(
            label_frame,
            text="",
            font=("Arial", 9),
            bg="lightgray"
        )
        self.header_label.pack()

        # Dropdown menu - Backdrop selector
        self.backdrop_options = tk.StringVar(value="Select Backdrop")
        self.backdrop_menu = tk.OptionMenu(btm_frame, self.backdrop_options,
                                           "Select Below")
        self.backdrop_menu.pack(side="left", padx=9)
        self.backdrop_menu['menu'].entryconfig(0, state="disabled")
        self.backdrop_menu['menu'].add_separator()
        self.backdrop_menu.configure(direction="above")

        self.add_backdrop_btn = tk.Button(btm_frame, text="Add Backdrop",
                                          command=self.add_backdrop_to_css,
                                          bd=3)
        self.add_backdrop_btn.pack(side="left", padx=7, pady=5)

        self.backdrop_entry = tk.Entry(btm_frame)
        self.backdrop_entry.pack(side="left", pady=5)

        # Calculate and set the entry box width to 75% of the window width
        def set_entry_width(event=None):
            window_width = self.root.winfo_width()
            entry_width = int(window_width * 0.75) // 9
            self.backdrop_entry.config(width=entry_width)

        # Bind the function to window resize event for dynamic adjustments
        self.root.bind("<Configure>", set_entry_width)

        set_entry_width()

    @staticmethod
    def toggle_stay_on_top(self):
        """
        Toggle whether the program window stays on top of other windows.
        """
        self.attributes("-topmost", not self.attributes("-topmost"))

    def open_github():
        """
        Open the project's Github page in user's default web browser.
        """
        webbrowser.open_new("https://github.com/StpME/VCThemeGUI")
