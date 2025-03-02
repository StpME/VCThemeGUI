from themes.dscplus import DSCPlusGUI
from themes.softx import SoftXGUI
import tkinter as tk


class GUISelector:
    """
    A GUI Selector to allow user to choose between
    different theme GUIS on program start.
    """
    def __init__(self, root, load_gui):
        """
        Initialize the GUISelector.

        Args:
            root (tk.Tk): The Tkinter window for the GUI selector.
            load_gui (function): The function to load the selected GUI.
        """
        self.root = root
        root.title("GUI Selector")
        root.minsize(300, 200)
        self.load_gui = load_gui

        width_base = 400
        height_base = 300
        width_window = self.root.winfo_screenwidth()
        height_window = self.root.winfo_screenheight()

        x = (width_window - width_base) // 2
        y = (height_window - height_base) // 2

        self.root.geometry(f"{width_base}x{height_base}+{x}+{y}")

        tk.Label(self.root, text="Select GUI to Load:").pack(padx=10)

        button_frame = tk.Frame(self.root)
        button_frame.pack(expand=True)

        # Discord+ button
        dsc_button = tk.Button(button_frame, text="Discord+",
                               command=lambda: self.load_gui("DSCPlusGUI"))
        dsc_button.pack(padx=10, pady=10)

        # SoftX button
        softx_button = tk.Button(button_frame, text="SoftX",
                                 command=lambda: self.load_gui("SoftXGUI"))
        softx_button.pack(padx=10, pady=10)


def main():
    """
    Initializes the Tkinter root window and starts the GUI theme selector.
    """
    root = tk.Tk()

    def load_gui(gui_name):
        """
        Callback function that handles GUI selection
        and loads the selected GUI.

        Args:
            gui_name (string): The name of the GUI class to load.
        """
        root.destroy()  # Destroy selector window
        new_root = tk.Tk()  # Create new root window for selected GUI

        # Set the new window to center of screen
        width_base = 900
        height_base = 500
        width_window = new_root.winfo_screenwidth()
        height_window = new_root.winfo_screenheight()
        x = (width_window - width_base) // 2
        y = (height_window - height_base) // 2
        new_root.geometry(f"{width_base}x{height_base}+{x}+{y}")

        # Dynamically load the selected GUI class
        if gui_name == "DSCPlusGUI":
            DSCPlusGUI(new_root)
        elif gui_name == "SoftXGUI":
            SoftXGUI(new_root)
        else:
            raise ValueError(f"Unknown value: {gui_name}")

    GUISelector(root, load_gui)
    root.mainloop()


if __name__ == "__main__":
    main()
