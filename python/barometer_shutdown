import tkinter as tk
from tkinter import simpledialog
import numpy as np
from timeflux.core.node import Node
import os
import json
import time

class VisualFeedback(Node):
    def __init__(self):
        super().__init__()
        self.start_time = time.time() 

        # Initialize the TKinter UI
        self.root = tk.Tk()
        self.root.title('Alpha Barometer')
        self.root.geometry("380x230")
        self.canvas = tk.Canvas(self.root, bg='white', width=360, height=210)
        self.canvas.pack(padx=10, pady=10)
        self._initialize_thresholds()
        self._draw_background()
        self._draw_colored_sectors()
        self.pointer = self.canvas.create_line(180, 160, 180, 40, fill='black', width=3, arrow=tk.LAST, arrowshape=(16, 20, 6))

    def _initialize_thresholds(self):
        directory_path = "/Users/Sophia/thresholds"  
        # List all JSON files in the directory
        json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
        # Sort files by modification time, newest first
        json_files.sort(key=lambda x: os.path.getmtime(os.path.join(directory_path, x)), reverse=True)

        if json_files:
            # Read the newest file
            newest_file_path = os.path.join(directory_path, json_files[0])
            with open(newest_file_path, "r") as file:
                thresholds = json.load(file)

            self.initial_thresholds = [thresholds["Upper"], thresholds["Middle Upper"],
                                    thresholds["Middle Lower"], thresholds["Lower"]]
            
            # Print the loaded thresholds
            print("Loaded Thresholds:")
            print(f"Upper: {self.initial_thresholds[0]}")
            print(f"Middle Upper: {self.initial_thresholds[1]}")
            print(f"Middle Lower: {self.initial_thresholds[2]}")
            print(f"Lower: {self.initial_thresholds[3]}")

        else:
            print("No threshold files found.")

    def _get_threshold(self, prompt):
        while True:
            user_input = simpledialog.askstring("Thresholds", prompt)
            try:
                threshold = float(user_input)
                return threshold
            except (ValueError, TypeError):
                print("Invalid input. Please enter a valid number.")

    def _get_pointer_properties(self, alpha_value):
        # Each tuple defines a value range, an angle range, and a color
        sectors = [
            ((self.initial_thresholds[1], self.initial_thresholds[0]), (0, 45), 'green'),  
            ((self.initial_thresholds[2], self.initial_thresholds[1]), (45, 90), 'yellow'),  
            ((self.initial_thresholds[3], self.initial_thresholds[2]), (90, 135), 'orange'),  
            ((0, self.initial_thresholds[3]), (135, 180), 'red')  
        ]

        # If the alpha value is above the upper threshold, set the pointer to the rightmost position of the green sector
        if alpha_value >= self.initial_thresholds[0]:
            return 45, 'green'

        for value_range, angle_range, color in sectors:
            if value_range[0] <= alpha_value < value_range[1]:
                value_span = value_range[1] - value_range[0]
                angle_span = angle_range[1] - angle_range[0]
                percentage = (alpha_value - value_range[0]) / value_span
                angle = angle_range[0] + percentage * angle_span
                return angle, color

        return 180, 'red'  # Default if no match (should not happen)

    def update(self):
    
        if time.time() - self.start_time >= 300:  # 300 seconds = 5 minutes
            print("5 minutes elapsed. Initiating shutdown.")
            self._shutdown_visual_feedback()
            
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

    def _draw_background(self):
        gradient = ["#f7f7f7", "#e5e5e5", "#d4d4d4", "#c2c2c2", "#b0b0b0"]
        for i, color in enumerate(gradient):
            self.canvas.create_arc(10+i, 10+i, 350-i, 310-i, start=0, extent=180, fill=color, outline="")

    def _draw_colored_sectors(self):
        sectors = [(0, 45, 'green'), (45, 45, 'yellow'), (90, 45, 'orange'), (135, 45, 'red')]
        for start, extent, color in sectors:
            self.canvas.create_arc(20, 20, 340, 300, start=start, extent=extent, fill=color, outline='')

    def _shutdown_visual_feedback(self):
        print("Shutting down Visual Feedback.")
        self.root.destroy()  # Close the tkinter window
        exit(0)  # Stop the script
