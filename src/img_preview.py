import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, UnidentifiedImageError
import requests
from io import BytesIO

class ImagePreview:
    def __init__(self, root, img_urls):
        self.root = root
        self.img_urls = img_urls
        self.img_labels = []

        # Canvas and scrollbar for image grid
        self.canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Load and display images
        self.load_imgs()

    # Checks for valid extensions on image urls so they can be displayed
    def is_valid_img_url(self, url):
        valid_extensions = [".gif", ".png", ".jpg", ".jpeg", ".bmp", ".webp"]
        return any(url.lower().endswith(ext) for ext in valid_extensions)

    # Loads images, skipping invalid or broken urls
    def load_imgs(self):
        for i, url in enumerate(self.img_urls):
            try:
                # Skip invalid URLs
                if not self.is_valid_img_url(url):
                    print(f"Skipping invalid image URL: {url}")
                    continue

                # Add headers to mimic a PC browser request so images can be properly displayed
                #  (may need extra testing)
                # Imgur and other sites may block site requests without valid User-Agents
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36"
                } # This is emulating a Chrome user on Windows 10 with compatibility

                # Fetch the image from the URL and check validity/status
                response = requests.get(url, headers=headers)
                response.raise_for_status()  

                # Check if the response contains valid image data
                if "image" not in response.headers.get("Content-Type", ""):
                    print(f"Skipping non-image URL: {url}")
                    continue

                # Load the image using Pillow/PIL
                img_data = response.content
                img = Image.open(BytesIO(img_data))
                img.thumbnail((150, 150))  # Resize the image to fit in the grid

                # Convert the the PIL image to Tkinter
                tk_img = ImageTk.PhotoImage(img)

                # Create a label to display the image
                img_label = tk.Label(self.scrollable_frame, image=tk_img)
                img_label.img = tk_img
                # Three columns per row (plan to make flex-auto)
                img_label.grid(row = i // 3, column = i % 3, padx = 5, pady = 5) 
                self.img_labels.append(img_label)
            except (requests.RequestException, UnidentifiedImageError) as e:
                print(f"Failed to load image from {url}: {e}")

    # Helper method to extract urls within the class
    def extract_img_urls(css_content):
        img_urls = []
        for line in css_content.split("\n"):
            if "--dplus-backdrop" in line and "url(" in line:
                # Extract the URL from the CSS line
                url = line.split("url(")[1].split(")")[0]
                img_urls.append(url)
        return img_urls