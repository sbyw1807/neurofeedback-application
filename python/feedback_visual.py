#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
from timeflux.core.node import Node
from timeflux.core.io import Port

class VisualFeedback(Node):

    def __init__(self, threshold=110):
        super().__init__()
        self._threshold = threshold

    def check_threshold(self, alpha_data):
        # Calculate the mean of the channels (columns) for each timepoint (row) using numpy
        alpha_mean_per_timepoint = np.mean(alpha_data, axis=1)
        print(alpha_mean_per_timepoint)
        # Provide feedback for each timepoint
        for value in alpha_mean_per_timepoint:
            print(f"Value: {value}, Threshold: {self._threshold}")
            if value > self._threshold:
                print("Threshold exceeded!")
            else:
                print("Threshold not exceeded.")

    def update(self):
        if self.i.ready():
            self.o = self.i  # Point output to same data object as input
            alpha_data = self.o.data
            if alpha_data is None:
                print("Received None data from input")
                return
            print(alpha_data.shape)
            print(alpha_data)
            self.check_threshold(alpha_data)

