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
        self.loaded_urls = set()

        # Create main frame that holds canvas and scrollbar so previews are loaded flexibly
        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True)
                        
        # Canvas and scrollbar for image grid
        self.canvas = tk.Canvas(main_frame)
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", self.update_scrollregion)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Load and display images
        self.load_imgs()

        # Bind resize event to adjust window layout with images
        root.bind("<Configure>", self.on_resize)

    # Checks for valid extensions on image urls so they can be displayed
    def is_valid_img_url(self, url):
        valid_extensions = [".gif", ".png", ".jpg", ".jpeg", ".bmp", ".webp"]
        return any(url.lower().endswith(ext) for ext in valid_extensions)

    # Loads images, checking and skipping invalid or broken urls
    def load_imgs(self):
        self.clear_existing_images()
        for i, url in enumerate(self.img_urls):
            if url not in self.loaded_urls:
                try:
                    # Skip invalid URLs
                    if not self.is_valid_img_url(url):
                        print(f"Skipping invalid image URL: {url}")
                        continue

                    # Add headers to mimic a PC browser request so images can be properly displayed
                    # Imgur and other sites may block site requests without valid User-Agents
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36"
                    } # This is emulating a Chrome user on Windows 10 with compatibility

                    # Fetch the image from the URL and check validity/status
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()  

                    # Check if the response contains valid image data
                    if "image" in response.headers.get("Content-Type", ""):
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
                        self.loaded_urls.add(url)  # Add URL to loaded URLs set
                        print(f"Loaded image {url} at row {i // self.get_num_columns()} and column {i % self.get_num_columns()}")
                    else: 
                        print(f"Skipping non-image URL: {url}")
                except (requests.RequestException, UnidentifiedImageError) as e:
                    print(f"Failed to load image from {url}: {e}")

        # Resize image previews after loaded for first time
        self.on_resize(None)
        self.update_scrollregion()

    # Clears images to avoid duped previews
    def clear_existing_images(self):
        for img_label in self.img_labels:
            img_label.grid_forget()
        self.img_labels = []
        self.loaded_urls = set() 
        print("Cleared existing images")

    # Helper method to extract urls within the class
    # *can't import method as they need sorted backdrops as a list instead of set
    def extract_img_urls(css_content):
        img_urls = []
        for line in css_content.split("\n"):
            if "--dplus-backdrop" in line and "url(" in line:
                # Extract the URL from the CSS line
                url = line.split("url(")[1].split(")")[0]
                img_urls.append(url)
        return img_urls
    
    # Update rows and cols and scrollbar region on dimension change event
    def on_resize(self, event):
        for i, img_label in enumerate(self.img_labels):
            img_label.grid(row=i // self.get_num_columns(), column=i % self.get_num_columns(), padx=5, pady=5)
        self.update_scrollregion()

    # Helper method to calculate num columns based on current width
    def get_num_columns(self):
        return max(1, self.root.winfo_width() // 160) 
    
    def update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
