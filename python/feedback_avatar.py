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
        self.root.geometry("850x350")
        self.canvas = tk.Canvas(self.root, bg='#f2f2f2', width=850, height=350, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

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
        if alpha_value < 100:
            prominent = "very_sad"
        elif 100 <= alpha_value < 110:
            prominent = "sad"
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
        if alpha_value < 100:
            status = "very_sad"
        elif 100 <= alpha_value < 110:
            status = "sad"
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

            alpha_mean_per_timepoint = np.mean(alpha_data, axis=1)
            for alpha_value in alpha_mean_per_timepoint:
                self._update_avatar(alpha_value)
                self.check_threshold(alpha_value)

            self.o.data = alpha_data
            self.root.update()

            print(alpha_data.shape)
            print(alpha_data)
