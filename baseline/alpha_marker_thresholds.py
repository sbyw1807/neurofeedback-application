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
                bins = np.linspace(min(self.alpha_values), max(self.alpha_values), 5)
                thresholds = {
                    "Lower": bins[1],
                    "Middle Lower": bins[2],
                    "Middle Upper": bins[3],
                    "Upper": bins[4]
                }

                timestamp = time.strftime("%Y%m%d%H%M%S")
                with open(f"{self.file_path}_{timestamp}.json", "w") as file:
                    json.dump(thresholds, file)
                print("Thresholds calculated and saved.")
