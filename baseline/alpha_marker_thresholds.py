import time
import numpy as np
import pandas as pd
import pylsl
from timeflux.core.node import Node

class AlphaMarker(Node):
    def __init__(self, sample_rate=2, duration=20, file_path="/Users/Sophia/thresholds/baseline_thresholds.txt"):
        super().__init__()
        self.sample_rate = sample_rate
        self.duration = duration
        self.file_path = file_path
        self.start_time = None
        self.alpha_values = []
        self.thresholds_calculated = False  # Flag to track if thresholds have been calculated
        self.stream_info = pylsl.StreamInfo('AlphaPower', 'Markers', 1, self.sample_rate, 'float32', 'alphamarker12345')
        self.outlet = pylsl.StreamOutlet(self.stream_info)

    def update(self):
        # Check if the node is receiving data
        if not self.i.ready():
            return

        # Start the timer and initialize data collection
        if self.start_time is None:
            self.start_time = time.time()
            print("Starting data collection for threshold calculation.")

        # Collect data for the specified duration
        if not self.thresholds_calculated and time.time() - self.start_time < self.duration:
            # Get alpha power values from the input data
            alpha_power_values = self.i.data.values[0]
            alpha_power_mean = np.mean(alpha_power_values)
            self.alpha_values.append(alpha_power_mean)

            # Push alpha value to the LSL outlet and output a DataFrame
            self.outlet.push_sample([alpha_power_mean])
            df = pd.DataFrame({'alpha_power': [alpha_power_mean]})
            self.o.set(df)
        elif not self.thresholds_calculated:
            # Process and save the collected alpha values only once
            self.thresholds_calculated = True  # Set the flag to true
            print("Threshold calculation initiated.")

            if self.alpha_values:
                # Calculate thresholds
                bins = np.linspace(min(self.alpha_values), max(self.alpha_values), 5) # min_value, max_value, num_bins+1 -> returns evenly spaced numbers over the specified interval
                thresholds = {
                    "Lower": bins[1],
                    "Middle Lower": bins[2],
                    "Middle Upper": bins[3],
                    "Upper": bins[4]
                }

                # Save thresholds to a file
                timestamp = time.strftime("%Y%m%d%H%M%S")
                with open(f"{self.file_path}_{timestamp}.txt", "w") as file:
                    for key, value in thresholds.items():
                        file.write(f"{key} Threshold: {value}\n")
                print("Thresholds calculated and saved.")
