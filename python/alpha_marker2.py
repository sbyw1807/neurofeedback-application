from timeflux.core.node import Node
import pylsl
import pandas as pd
import numpy as np

class AlphaMarker(Node):
    def __init__(self, sample_rate=2, channels=19):
        super().__init__()
        self.sample_rate = sample_rate
        self.channels = channels
        self.stream_info = pylsl.StreamInfo('AlphaPower', 'Markers', self.channels, self.sample_rate, 'float32', 'alphamarker12345')
        self.outlet = pylsl.StreamOutlet(self.stream_info)
    
    def update(self):
        if self.i.ready():
            # Get the alpha power values for all channels from the input data
            # Assuming each row in your data represents a timepoint and each column represents a channel
            alpha_power_values = self.i.data.values[0]  # A single sample with 130 channel values

            # Push the alpha values to the LSL outlet
            self.outlet.push_sample(alpha_power_values)

            # Create and output a DataFrame with the alpha values (timestamp will be added by LSL)
            # Here, each row represents a timepoint, and columns represent alpha values for each channel
            column_names = [f'alpha_{i}' for i in range(self.channels)]
            df = pd.DataFrame([alpha_power_values], columns=column_names)
            self.o.set(df)
