from themes.dscplus import DSCPlusGUI
from themes.softx import SoftXGUI
import tkinter as tk


class GUISelector:
    """
    A GUI Selector to allow user to choose between
    different theme GUIS on program start.
    """
    def __init__(self, root):
        """
        Initialize the GUISelector.

        Args:
            root (tk.Tk): The Tkinter window for the GUI selector.
        """
        self.root = root
        root.title("GUI Selector")
        root.minsize(300, 200)

        width_base = 400
        height_base = 300
        width_window = self.root.winfo_screenwidth()
        height_window = self.root.winfo_screenheight()

        x = (width_window - width_base) // 2
        y = (height_window - height_base) // 2

        # Set selector to center of window
        self.root.geometry(f"{width_base}x{height_base}+{x}+{y}")

        tk.Label(self.root, text="Select GUI to Load:").pack(padx=10)

        button_frame = tk.Frame(self.root)
        button_frame.pack(expand=True)

        dsc_button = tk.Button(button_frame, text="Discord+",
                               command=self.load_dsc_gui)
        dsc_button.pack(padx=10, pady=10)

        softx_button = tk.Button(button_frame, text="SoftX",
                                 command=self.load_softx_gui)
        softx_button.pack(padx=10, pady=10)

    def load_dsc_gui(self):
        """
        Loads the Discord+ GUI.

        Destroys the current window and initializes a new Tkinter window
        for the GUI.
        """
        self.root.destroy()
        root = tk.Tk()
        root.minsize(600, 400)

        width_base = 900
        height_base = 500
        width_window = root.winfo_screenwidth()
        height_window = root.winfo_screenheight()

        x = (width_window - width_base) // 2
        y = (height_window - height_base) // 2

        # Set the new window to center of screen
        root.geometry(f"{width_base}x{height_base}+{x}+{y}")

        DSCPlusGUI(root)

    def load_softx_gui(self):
        """
        Loads the SoftX GUI.

        Destroys the current window and initializes a new Tkinter window
        for the GUI.
        """
        self.root.destroy()
        root = tk.Tk()
        root.minsize(600, 400)

        width_base = 900
        height_base = 500
        width_window = root.winfo_screenwidth()
        height_window = root.winfo_screenheight()

        x = (width_window - width_base) // 2
        y = (height_window - height_base) // 2

        # Set the new window to center of screen
        root.geometry(f"{width_base}x{height_base}+{x}+{y}")
        SoftXGUI(root)


def main():
    """
    Initializes the Tkinter root window and starts the GUI theme selector.
    """
    root = tk.Tk()
    GUISelector(root)
    root.mainloop()


if __name__ == "__main__":
    main()
