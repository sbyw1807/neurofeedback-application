from timeflux.core.node import Node
import pylsl
import pandas as pd
import numpy as np

class BetaMarker(Node):
    def __init__(self, sample_rate=2):
        super().__init__()
        self.sample_rate = sample_rate
        self.stream_info = pylsl.StreamInfo('BetaPower', 'Markers', 1, self.sample_rate, 'float32', 'betamarker12345')
        self.outlet = pylsl.StreamOutlet(self.stream_info)
    
    def update(self):
        if self.i.ready():
            # Get the beta power values for all channels from the input data
            beta_power_values = self.i.data.values[0] 

            # Calculate the mean of beta power values
            beta_power_mean = np.mean(beta_power_values)

            # Push only the beta value to the LSL outlet
            self.outlet.push_sample([beta_power_mean])

            # Output a DataFrame with the beta value (timestamp will be added by LSL)
            df = pd.DataFrame({'beta_power': [beta_power_mean]})
            self.o.set(df)
