
import tkinter as tk
import numpy as np
from timeflux.core.node import Node

class VisualFeedback(Node):

    def __init__(self):
        super().__init__()

        # Initialize the TKinter UI
        self.root = tk.Tk()
        self.root.title('Alpha Barometer')
        self.root.geometry("380x230")
        self.canvas = tk.Canvas(self.root, bg='white', width=360, height=210)
        self.canvas.pack(padx=10, pady=10)
        self._draw_background()
        self._draw_colored_sectors()
        self.pointer = self.canvas.create_line(180, 160, 180, 40, fill='black', width=3, arrow=tk.LAST, arrowshape=(16, 20, 6))

    def _draw_background(self):
        gradient = ["#f7f7f7", "#e5e5e5", "#d4d4d4", "#c2c2c2", "#b0b0b0"]
        for i, color in enumerate(gradient):
            self.canvas.create_arc(10+i, 10+i, 350-i, 310-i, start=0, extent=180, fill=color, outline="")

    def _draw_colored_sectors(self):
        sectors = [(0, 45, 'green'), (45, 45, 'yellow'), (90, 45, 'orange'), (135, 45, 'red')] # starting angle ( 0 degrees is rightmost point, angles increase counterclockwise), extent, color 
        for start, extent, color in sectors:
            self.canvas.create_arc(20, 20, 340, 300, start=start, extent=extent, fill=color, outline='')

    def _get_pointer_properties(self, alpha_value):
        # Each tuple defines a value range, an angle range, and a color
        sectors = [
            ((0, 100), (135, 180), 'red'),
            ((100, 110), (90, 135), 'orange'),
            ((110, 120), (45, 90), 'yellow'),
            ((120, 200), (0, 45), 'green')
        ]
        
        for value_range, angle_range, color in sectors:
            if value_range[0] <= alpha_value < value_range[1]:
                value_span = value_range[1] - value_range[0]
                angle_span = angle_range[1] - angle_range[0]
                percentage = (alpha_value - value_range[0]) / value_span # percentage of how far alpha_value is within the value rang
                angle = angle_range[0] + percentage * angle_span # result is angle at which pointer should point 
                return angle, color

        return 180, 'red'  # Default if no match (should not happen)

    def update(self):
        self.o = self.i  # Point output to same data object as input
        alpha_data = self.i.data
        if alpha_data is None:
            return
        # Display the values and check threshold
        print(alpha_data.shape)
        print(alpha_data)
        
        # Update the barometer pointer
        alpha_mean_per_timepoint = np.mean(alpha_data, axis=1)
        for mean_alpha in alpha_mean_per_timepoint:
            angle, color = self._get_pointer_properties(mean_alpha)
            print(f"Value: {mean_alpha}, Color: {color}")
            self._update_pointer(angle)
        
        # Pass the data through
        self.o.data = alpha_data
        
        self.root.update()

    def _update_pointer(self, angle):  # Now, this function accepts an angle directly
        print(f"Received angle: {angle}")  

        rad = angle * (np.pi / 180)
        end_x = 180 + 120 * np.cos(rad)
        end_y = 160 - 120 * np.sin(rad)
        self.canvas.coords(self.pointer, 180, 160, end_x, end_y)
