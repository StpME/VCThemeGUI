import tkinter as tk
class Setup:
    REPO = "StpME/VCThemeGUI"
    EXE_NAME = "VCTheme.exe"

    def setup_gui(self, gui_name):
        # GUI main headers
        self.label = tk.Label(self.root, text=("Select " + gui_name + " theme CSS file"), font=("Arial", 12))
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

        self.backdrop_menu['menu'].entryconfig(0, state="disabled") # Set first descriptor option to disabled
        self.backdrop_menu['menu'].add_separator()

        # Backdrop frame for button and entry box
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, anchor=tk.SW, fill=tk.X, padx=5, pady=5)

        # Add backdrop button
        self.add_backdrop_btn = tk.Button(self.bottom_frame, text="Add Backdrop", 
                                        command=self.add_backdrop_to_css,
                                        bd=3 # Border width
                                    )
        self.add_backdrop_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Backdrop entry/input box
        self.backdrop_entry = tk.Entry(self.bottom_frame, width=50)
        self.backdrop_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Calculate and set the entry box width to 75% of the window width
        def set_entry_width(event=None):
            window_width = self.root.winfo_width()
            entry_width = int(window_width * 0.75) // 9
            self.backdrop_entry.config(width = entry_width)

        # Bind the function to window resize event for dynamic adjustments
        self.root.bind("<Configure>", set_entry_width)

        set_entry_width()