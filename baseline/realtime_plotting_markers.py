import time
import pyqtgraph as pg
from pylsl import StreamInlet, resolve_stream
from collections import deque
import numpy as np

# Resolve the alpha power stream
print("Looking for streams of type 'Markers'...")
streams = resolve_stream('type', 'Markers')

# Print information about the detected stream
if streams:
    stream_info = streams[0]
    print("Detected Stream Info:")
    print("Name:", stream_info.name())
    print("Type:", stream_info.type())
    print("Channels:", stream_info.channel_count())
    print("Sample Rate:", stream_info.nominal_srate())
else:
    print("No suitable stream found.")

# Assuming your stream is the first one found
inlet = StreamInlet(streams[0]) if streams else None

# Initialize pyqtgraph
app = pg.mkQApp("Alpha Power Visualization") if inlet else None
win = pg.GraphicsLayoutWidget(show=True, title="Real Time Alpha Power") if inlet else None
plot = win.addPlot(title="Alpha Power") if inlet else None
curve = plot.plot(pen='y') if inlet else None

# Add grid
plot.showGrid(x=True, y=True, alpha=0.5)

# Set axis labels
plot.setLabel('left', 'Alpha Power')
plot.setLabel('bottom', 'Time', units='s')

# Set title
plot.setTitle('Real Time Alpha Power Monitoring')

# Initialize a fixed-size buffer for data
buffer_size = 500  # Adjust this to how many points you want to display at once
data_buffer = deque(maxlen=buffer_size)
time_buffer = deque(maxlen=buffer_size)

# Use the current time to set an initial value for the x-axis
start_time = time.time()

def update():
    print("Updating plot...")
    global start_time
    sample, timestamp = inlet.pull_sample(timeout=0.0) if inlet else (None, None)
    if sample:
        # Update the start time only once
        if not time_buffer:
            start_time = time.time()

        # Calculate the elapsed time since the start of the plotting
        elapsed_time = time.time() - start_time
        print("Received sample:", sample, "at time:", elapsed_time)

        # Append the new data to the buffers
        time_buffer.append(elapsed_time)
        data_buffer.append(sample[0])

        # Update the plot with the data in the buffers
        curve.setData(np.array(time_buffer), np.array(data_buffer))

# Update the plot every 500 ms
timer = pg.QtCore.QTimer() if inlet else None
if timer:
    timer.timeout.connect(update)
    timer.start(500)  
    app.exec_()
else:
    print("No suitable stream found.")
