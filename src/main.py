from dscplus import DSCPlusGUI
from softx import SoftXGUI
import tkinter as tk
class GUISelector:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI Selector")

        
        width_base = 400
        height_base = 300
        width_window = self.root.winfo_screenwidth()
        height_window = self.root.winfo_screenheight()

        x = (width_window - width_base) // 2  
        y = (height_window - height_base) // 2  
        
        # Set selector to center of window 
        self.root.geometry(f"{width_base}x{height_base}+{x}+{y}")
        
        tk.Label(self.root, text="Select GUI to Load:").pack(padx=10)

        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(expand=True)

        dsc_button = tk.Button(button_frame, text="DSCPlusGUI", command=self.load_dsc_gui)
        dsc_button.pack(padx=10, pady=10)  

        softx_button = tk.Button(button_frame, text="SoftXGUI", command=self.load_softx_gui)
        softx_button.pack(padx=10, pady=10)

    def load_dsc_gui(self):
        self.root.destroy()
        root = tk.Tk()
        root.minsize(600,400)

        width_base = 900 
        height_base = 500
        width_window = root.winfo_screenwidth()
        height_window = root.winfo_screenheight()

        x = (width_window - width_base) // 2
        y = (height_window - height_base) // 2

        # Set the new window to center of screen with same dimensions
        root.geometry(f"{width_base}x{height_base}+{x}+{y}")

        app = DSCPlusGUI(root)

    def load_softx_gui(self):
        self.root.destroy()
        root = tk.Tk()
        root.minsize(600,400)

        width_base = 900 
        height_base = 500
        width_window = root.winfo_screenwidth()
        height_window = root.winfo_screenheight()

        x = (width_window - width_base) // 2
        y = (height_window - height_base) // 2

        # Set the new window to center of screen with same dimensions
        root.geometry(f"{width_base}x{height_base}+{x}+{y}")
        app = SoftXGUI(root)

def main():
    root = tk.Tk()
    app = GUISelector(root)
    root.mainloop()

if __name__ == "__main__":
    main()
