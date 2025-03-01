import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, UnidentifiedImageError
import requests
from io import BytesIO


class ImagePreview:
    """
    A class to display image previews of backdrop urls in a scrollable grid.
    """
    def __init__(self, root, img_urls, onclick=None):
        """
        Initialize the ImagePreview with the root window and image urls.

        Args:
            root (tk.Tk): The window for the image preview.
            img_urls (list): A list of image URLs to be displayed.
            onclick (function): Function called when image is clicked (event).
        """
        self.root = root
        self.img_urls = img_urls
        self.img_labels = []
        self.loaded_urls = set()
        self.preview_size = (125, 100)  # Set fixed size for all previews
        self.onclick = onclick

        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(main_frame)
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical",
                                       command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", self.update_scrollregion)
        self.canvas.create_window((0, 0), window=self.scrollable_frame,
                                  anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind the mouse scroll wheel to canvas to scroll images
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        self.load_images()

        # Bind resize event to adjust window layout with images
        root.bind("<Configure>", self.on_resize)

    def is_valid_image_url(self, url):
        """
        Check if the url has a valid, supported image extension.

        Args:
            url (string): The url to check.

        Returns:
            (boolean): True if the url has a valid extension, False otherwise.
        """
        valid_extensions = [".gif", ".png", ".jpg", ".jpeg", ".bmp", ".webp"]
        return any(url.lower().endswith(ext) for ext in valid_extensions)

    def load_images(self):
        """
        Load the images from the provided urls and display them in the grid.
        Checks for valid image urls and skips invalid or broken urls.
        """
        self.clear_existing_images()
        for i, url in enumerate(self.img_urls):
            if url not in self.loaded_urls:
                try:
                    # Skip invalid URLs
                    if not self.is_valid_image_url(url):
                        print(f"Skipping invalid image URL: {url}")
                        continue

                    # Add headers to mimic a PC browser request so
                    # images can be properly displayed
                    # Imgur & other sites block requests w/o valid User-Agents
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; "
                        "x64) AppleWebKit/537.36 "
                        "Chrome/91.0.4472.124 Safari/537.36"
                    }  # Emulating a Chrome user on Windows 10

                    # Fetch the image from the URL and check validity/status
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()

                    # Check if the response contains valid image data
                    if "image" in response.headers.get("Content-Type", ""):
                        # Load the image using Pillow/PIL
                        img_data = response.content
                        img = Image.open(BytesIO(img_data))
                        img = self.resize_and_crop(img, self.preview_size)
                        img.thumbnail((150, 150))  # Resize img to fit
                        # Convert the the PIL image to Tkinter
                        tk_img = ImageTk.PhotoImage(img)
                        # Create a label to display the image
                        img_label = tk.Label(self.scrollable_frame,
                                             image=tk_img)
                        img_label.img = tk_img
                        img_label.url = url

                        # Clickable previews
                        if self.onclick:
                            img_label.bind("<Button-1>", lambda e,
                                           u=url: self.onclick(u))

                        img_label.grid(row=i // 3, column=i % 3,
                                       padx=5, pady=5)
                        self.img_labels.append(img_label)
                        self.loaded_urls.add(url)
                        print(f"Loaded image {url} at row "
                              f"{i // self.get_num_columns()} and column "
                              f"{i % self.get_num_columns()}")
                    else:
                        print(f"Skipping non-image URL: {url}")
                except (requests.RequestException,
                        UnidentifiedImageError) as e:
                    print(f"Failed to load image from {url}: {e}")

        # Resize image previews after loaded for first time
        self.on_resize(None)
        self.update_scrollregion()

    def resize_and_crop(self, img, size):
        """
        Resize and crop given image to fit the target size.

        Args:
            img (PIL.Image): The image to resize and crop.
            size (tuple): The target size (width, height).

        Returns:
            img (PIL.Image): The resized and cropped image.
        """
        # Calculate the images aspect ratio
        img_ratio = img.width / img.height
        target_ratio = size[0] / size[1]

        if img_ratio > target_ratio:  # if wider
            new_height = size[1]
            new_width = int(new_height * img_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            left = (img.width - size[0]) / 2
            right = left + size[0]
            img = img.crop((left, 0, right, size[1]))
        else:  # if taller
            new_width = size[0]
            new_height = int(new_width / img_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            top = (img.height - size[1]) / 2
            bottom = top + size[1]
            img = img.crop((0, top, size[0], bottom))

        return img

    def clear_existing_images(self):
        """
        Clear the existing image previews from the grid.
        Ensures no image previews are duplicated when reloading images.
        """
        for img_label in self.img_labels:
            img_label.grid_forget()
        self.img_labels = []
        self.loaded_urls = set()
        print("Cleared existing images")

    def highlight_image(self, url):
        """
        Highlight the image with the provided url in the grid.

        Args:
            url (string): The url of the image to highlight.
        """
        for img_label in self.img_labels:
            # Reset styling
            img_label.config(borderwidth=0, highlightthickness=0)
            # Highlight the currently selected image with a border
            if hasattr(img_label, "url") and img_label.url == url:
                img_label.config(highlightbackground="blue",
                                 highlightthickness=4)

    def extract_image_urls(css_content, theme_format):
        """
        Extract image urls from the provided CSS content.

        Args:
            css_content (string): The CSS text to extract urls from.
            theme_format (string): The theme format to search for.

        Returns:
            img_urls (list): A list of image urls
                             extracted from the CSS content.
        """
        img_urls = []
        for line in css_content.split("\n"):
            if theme_format in line and "url(" in line:
                # Extract the URL from the CSS line
                url = line.split("url(")[1].split(")")[0]
                img_urls.append(url)
        return img_urls

    def on_resize(self, event):
        """
        Update the number of columns based on current window width.
        Adjusts the grid layout and scrollbar region accordingly.

        Args:
            event (tk.Event): The window resize event.
        """
        for i, img_label in enumerate(self.img_labels):
            img_label.grid(row=i // self.get_num_columns(),
                           column=i % self.get_num_columns(),
                           padx=5, pady=5, sticky="nsew")
        self.update_scrollregion()

    def get_num_columns(self):
        """
        Calculate the number of columns based on the current window width.

        Returns:
            num_cols (int): The number of columns to display in the grid
        """
        # Calculate the available width for the grid
        scrollbar_width = self.scrollbar.winfo_width()
        avail_width = self.root.winfo_width() - scrollbar_width

        # Calculate the width of each image preview (including ~x padding)
        img_width = self.preview_size[0] + 10

        num_columns = max(1, avail_width // img_width)
        return num_columns

    def update_scrollregion(self, event=None):
        """
        Updates the scroll region of the canvas to fit the content.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        """
        Handle mouse wheel events for scrolling the image grid.

        Args:
            event (tk.Event): The mouse wheel (scrolling) event.
        """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
