from timeflux.core.node import Node
import pylsl
import pandas as pd
import numpy as np

class ThetaMarker(Node):
    def __init__(self, sample_rate=2):
        super().__init__()
        self.sample_rate = sample_rate
        self.stream_info = pylsl.StreamInfo('ThetaPower', 'Markers', 1, self.sample_rate, 'float32', 'thetamarker12345')
        self.outlet = pylsl.StreamOutlet(self.stream_info)
    
    def update(self):
        if self.i.ready():
            # Get the theta power values for all channels from the input data
            theta_power_values = self.i.data.values[0]  

            # Calculate the mean of theta power values
            theta_power_mean = np.mean(theta_power_values)

            # Push only the theta value to the LSL outlet
            self.outlet.push_sample([theta_power_mean])

            # Output a DataFrame with the theta value (timestamp will be added by LSL)
            df = pd.DataFrame({'theta_power': [theta_power_mean]})
            self.o.set(df)

