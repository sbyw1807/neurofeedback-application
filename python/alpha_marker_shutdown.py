from timeflux.core.node import Node
import pylsl
import pandas as pd
import numpy as np
import time

class AlphaMarker(Node):
    def __init__(self, sample_rate=2):
        super().__init__()
        self.sample_rate = sample_rate
        self.stream_info = pylsl.StreamInfo('AlphaPower', 'Markers', 1, self.sample_rate, 'float32', 'alphamarker12345')
        self.outlet = pylsl.StreamOutlet(self.stream_info)
        self.start_time = None
    
    def update(self):
        if not self.start_time:
            self.start_time = time.time()

        elapsed_time = time.time() - self.start_time
        if elapsed_time >= 300:  # 300 seconds = 5 minutes
            self.logger.info("5 minutes elapsed. Initiating shutdown.")
            self._shutdown_timeflux()

        if self.i.ready():
            # Get the alpha power values for all channels from the input data
            alpha_power_values = self.i.data.values[0]  # Assuming you have a single sample

            # Calculate the mean of alpha power values
            alpha_power_mean = np.mean(alpha_power_values)

            # Push only the alpha value to the LSL outlet
            self.outlet.push_sample([alpha_power_mean])

            # Output a DataFrame with the alpha value (timestamp will be added by LSL)
            df = pd.DataFrame({'alpha_power': [alpha_power_mean]})
            self.o.set(df)

    def _shutdown_timeflux(self):
        self.logger.info("Shutting down Timeflux.")
        exit(0)  