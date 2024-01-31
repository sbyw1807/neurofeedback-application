import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import numpy as np
from timeflux.core.node import Node
import os
import json
import time

class VisualFeedbackAvatar(Node):

    def __init__(self, threshold_dir="/Users/Sophia/thresholds"):
        super().__init__()

        # Initialize the TKinter UI for Avatar
        self.root = tk.Tk()
        self.root.title('Avatar Feedback')
        self.root.geometry("850x350")
        self.canvas = tk.Canvas(self.root, bg='#f2f2f2', width=850, height=350, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        self.start_time = time.time() 
        
        # Load threshold values
        self.thresholds = self._load_latest_thresholds(threshold_dir)
        if self.thresholds:
            print(f"Loaded Thresholds:\n{self.thresholds}")

        # Load images using PIL
        self.raw_images = {
            "very_sad": Image.open("very_sad.png"),
            "sad": Image.open("sad.png"),
            "happy": Image.open("happy.png"),
            "very_happy": Image.open("very_happy.png")
        }

        self.images = {}
        self.image_positions = {
            "very_sad": (140, 175),
            "sad": (280, 175),
            "happy": (420, 175),
            "very_happy": (560, 175)
        }

    def _load_latest_thresholds(self, directory_path):
        json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
        json_files.sort(key=lambda x: os.path.getmtime(os.path.join(directory_path, x)), reverse=True)

        if not json_files:
            raise FileNotFoundError("No threshold files found in the specified directory.")

        newest_file_path = os.path.join(directory_path, json_files[0])
        with open(newest_file_path, "r") as file:
            return json.load(file)

    def update_images(self, prominent):
        for name, image in self.raw_images.items():
            if name == prominent:
                image = image.resize((180, 180))
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.2)
            else:
                image = image.resize((120, 120))
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(0.7)

            self.images[name] = ImageTk.PhotoImage(image)

    def _update_avatar(self, alpha_value):
        lower_threshold = self.thresholds["Lower"]
        middle_lower_threshold = self.thresholds["Middle Lower"]
        middle_upper_threshold = self.thresholds["Middle Upper"]
        upper_threshold = self.thresholds["Upper"]

        if alpha_value < middle_lower_threshold:
            prominent = "very_sad"
        elif middle_lower_threshold <= alpha_value < middle_upper_threshold:
            prominent = "sad"
        elif middle_upper_threshold <= alpha_value < upper_threshold:
            prominent = "happy"
        else:
            prominent = "very_happy"

        self.update_images(prominent)
        self.canvas.delete("all")

        # Display the updated image
        image_to_display = self.images[prominent]
        x, y = self.image_positions[prominent]
        self.canvas.create_image(x, y, image=image_to_display, anchor='center')

        self.root.update()

    def check_threshold(self, alpha_value):
        lower_threshold = self.thresholds["Lower"]
        middle_lower_threshold = self.thresholds["Middle Lower"]
        middle_upper_threshold = self.thresholds["Middle Upper"]
        upper_threshold = self.thresholds["Upper"]

        if alpha_value < middle_lower_threshold:
            status = "very_sad"
        elif middle_lower_threshold <= alpha_value < middle_upper_threshold:
            status = "sad"
        elif middle_upper_threshold <= alpha_value < upper_threshold:
            status = "happy"
        else:
            status = "very_happy"

        print(f"Alpha value: {alpha_value}, Status: {status}")
        
    def update(self):
        
        current_time = time.time()

        if current_time - self.start_time >= 300:  # 300 seconds = 5 minutes
            print("5 minutes elapsed. Initiating shutdown.")
            self._shutdown_visual_feedback_avatar()
            
        if self.i.ready():
            alpha_data = self.i.data
            if alpha_data is None:
                return

            alpha_mean_per_timepoint = np.mean(alpha_data, axis=1)
            for alpha_value in alpha_mean_per_timepoint:
                self._update_avatar(alpha_value)
                self.check_threshold(alpha_value)

            self.o.data = alpha_data
            self.root.update()

            print(alpha_data.shape)
            print(alpha_data)
    
    def _shutdown_visual_feedback_avatar(self):
        print("Shutting down Visual Feedback Avatar.")
        self.root.destroy()  # Close the tkinter window
        exit(0)  # Stop the script
