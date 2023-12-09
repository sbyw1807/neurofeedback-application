import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import numpy as np
from timeflux.core.node import Node

class VisualFeedbackAvatar(Node):

    def __init__(self):
        super().__init__()

        # Initialize the TKinter UI for Avatar
        self.root = tk.Tk()
        self.root.title('Avatar Feedback')
        self.root.geometry("850x350")  # Increased width and height to accommodate larger avatars
        self.canvas = tk.Canvas(self.root, bg='#f2f2f2', width=850, height=350, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        # Load images using PIL
        self.raw_images = {
            "very_sad": Image.open("very_sad.png"),
            "sad": Image.open("sad.png"),
            "neutral": Image.open("natural.png"),
            "happy": Image.open("happy.png"),
            "very_happy": Image.open("very_happy.png")
        }

        self.images = {} # stores resized and enhanced images 
        self.image_positions = {
            "very_sad": (60, 175),
            "sad": (210, 175),
            "neutral": (360, 175),
            "happy": (510, 175),
            "very_happy": (660, 175)
        }

        self.update_images("neutral")  # Default to neutral

    def update_images(self, prominent):
        # prominent expression is given a larger and brighter image while the others are made smaller and darker 
        for name, image in self.raw_images.items():
            if name == prominent:
                image = image.resize((180, 180))  # Increased size
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.2)
            else:
                image = image.resize((120, 120))  # Increased size
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(0.7)

            self.images[name] = ImageTk.PhotoImage(image)

    def _update_avatar(self, alpha_value):
        if alpha_value < 90:
            prominent = "very_sad"
        elif 90 <= alpha_value < 100:
            prominent = "sad"
        elif 100 <= alpha_value < 110:
            prominent = "neutral"
        elif 110 <= alpha_value < 120:
            prominent = "happy"
        else:
            prominent = "very_happy"

        self.update_images(prominent)
        self.canvas.delete("all")
        for name, image in self.images.items():
            x, y = self.image_positions[name]
            self.canvas.create_image(x, y, image=image)

        self.root.update()

    def check_threshold(self, alpha_value):
        if alpha_value < 90:
            status = "very_sad"
        elif 90 <= alpha_value < 100:
            status = "sad"
        elif 100 <= alpha_value < 110:
            status = "neutral"
        elif 110 <= alpha_value < 120:
            status = "happy"
        else:
            status = "very_happy"

        print(f"Alpha value: {alpha_value}, Status: {status}")
        
    def update(self):
        if self.i.ready():
            alpha_data = self.i.data
            if alpha_data is None:
                return

            # Calculate the mean alpha value for each timepoint
            alpha_mean_per_timepoint = np.mean(alpha_data, axis=1)
            for alpha_value in alpha_mean_per_timepoint:
                self._update_avatar(alpha_value)
                self.check_threshold(alpha_value)  # Checking the threshold here

            # Point output to the same data object as input
            self.o.data = alpha_data

            # Update the visual avatar representation
            self.root.update()

            # Display the values (if you still want this)
            print(alpha_data.shape)
            print(alpha_data)
