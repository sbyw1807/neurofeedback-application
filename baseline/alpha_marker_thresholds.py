import time
import numpy as np
import pandas as pd
import pylsl
from timeflux.core.node import Node
import json

class AlphaMarker(Node):
    def __init__(self, sample_rate=2, duration=300, file_path="/Users/Sophia/thresholds/baseline_thresholds.json"):
        super().__init__()
        self.sample_rate = sample_rate
        self.duration = duration
        self.file_path = file_path
        self.start_time = None
        self.alpha_values = []
        self.thresholds_calculated = False  # Flag to track if thresholds have been calculated
        self.stream_info = pylsl.StreamInfo('AlphaPower', 'Markers', 1, self.sample_rate, 'float32', 'alphamarker12345')
        self.outlet = pylsl.StreamOutlet(self.stream_info)
        print("Data capturing initialized for AlphaMarker.")

    def update(self):
        if not self.i.ready():
            return

        current_time = time.time()

        if self.start_time is None:
            self.start_time = current_time
            self.last_update_time = current_time
            print("Starting data collection for threshold calculation.")

        if not self.thresholds_calculated and current_time - self.start_time < self.duration:
            # Regular update every 10 seconds
            if current_time - self.last_update_time >= 10:
                print(f"Data capturing in progress... {int(current_time - self.start_time)} seconds elapsed.")
                self.last_update_time = current_time

            alpha_power_values = self.i.data.values[0]
            alpha_power_mean = np.mean(alpha_power_values)
            self.alpha_values.append(alpha_power_mean)

            self.outlet.push_sample([alpha_power_mean])
            df = pd.DataFrame({'alpha_power': [alpha_power_mean]})
            self.o.set(df)

        elif not self.thresholds_calculated:
            self.thresholds_calculated = True
            print("Threshold calculation initiated.")

            if self.alpha_values:
                # Data Smoothing (e.g., Moving Average)
                smoothed_values = pd.Series(self.alpha_values).rolling(window=5, min_periods=1).mean()

                # Outlier Removal (using IQR)
                Q1 = np.percentile(smoothed_values, 25)
                Q3 = np.percentile(smoothed_values, 75)
                IQR = Q3 - Q1
                filtered_values = smoothed_values[~((smoothed_values < (Q1 - 1.5 * IQR)) | (smoothed_values > (Q3 + 1.5 * IQR)))]

                # Percentile-Based Thresholds
                thresholds = {
                    "Lower": np.percentile(filtered_values, 25),
                    "Middle Lower": np.percentile(filtered_values, 50),  # Median
                    "Middle Upper": np.percentile(filtered_values, 75),
                    "Upper": np.percentile(filtered_values, 95)  # Higher percentile for upper limit
                }

                timestamp = time.strftime("%Y%m%d%H%M%S")
                with open(f"{self.file_path}_{timestamp}.json", "w") as file:
                    json.dump(thresholds, file)
                print("Thresholds calculated and saved.")
