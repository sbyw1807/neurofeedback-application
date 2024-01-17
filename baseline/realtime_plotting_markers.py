import sys
import time
import numpy as np
from pylsl import StreamInlet, resolve_stream
import pyqtgraph as pg
from collections import deque
from PyQt5.QtCore import Qt  

# Initialize PyQtGraph with enhanced aesthetics
app = pg.mkQApp("LSL Stream Visualization")
win = pg.GraphicsLayoutWidget(show=True, title="Real-Time Stream Visualization")
plot = win.addPlot(title="Stream Data")
plot.setLabel('left', 'Amplitude')
plot.setLabel('bottom', 'Time (s)')
plot.getAxis("left").tickFont = pg.QtGui.QFont("Arial", 12)
plot.getAxis("bottom").tickFont = pg.QtGui.QFont("Arial", 12)
plot.addLegend(offset=(30, 30))

# Customize the legend
legend = plot.legend
legend.setAutoFillBackground(False)
legend.setFont(pg.QtGui.QFont("Arial", 12))

# Create curves for each stream with new colors and line styles
alpha_curve = plot.plot(pen=pg.mkPen(color='b', width=2), name='Alpha Power')
theta_curve = plot.plot(pen=pg.mkPen(color=(148, 0, 211), style=Qt.DashLine, width=2), name='Theta Power')
beta_curve = plot.plot(pen=pg.mkPen(color='turquoise', style=Qt.DotLine, width=2), name='Beta Power')

# Resolve LSL streams
def resolve_lsl_stream(stream_name):
    print(f"Looking for {stream_name} stream...")
    streams = resolve_stream('name', stream_name)
    if not streams:
        print(f"{stream_name} stream not found.")
        sys.exit(1)
    return StreamInlet(streams[0])

alpha_inlet = resolve_lsl_stream('AlphaPower')
theta_inlet = resolve_lsl_stream('ThetaPower')
beta_inlet = resolve_lsl_stream('BetaPower')

# Buffer for the plot
buffer_size = 500
alpha_data = deque(maxlen=buffer_size)
theta_data = deque(maxlen=buffer_size)
beta_data = deque(maxlen=buffer_size)
time_data = deque(maxlen=buffer_size)

# Start time for the x-axis
start_time = time.time()

def update():
    # Pull sample from each stream
    alpha_sample, _ = alpha_inlet.pull_sample(timeout=0.0)
    theta_sample, _ = theta_inlet.pull_sample(timeout=0.0)
    beta_sample, _ = beta_inlet.pull_sample(timeout=0.0)

    new_data = False

    if alpha_sample:
        alpha_data.append(alpha_sample[0])
        new_data = True
    if theta_sample:
        theta_data.append(theta_sample[0])
        new_data = True
    if beta_sample:
        beta_data.append(beta_sample[0])
        new_data = True

    if new_data:
        current_time = time.time() - start_time
        time_data.append(current_time)

        # Update the plots
        alpha_curve.setData(np.array(time_data), np.array(alpha_data))
        theta_curve.setData(np.array(time_data), np.array(theta_data))
        beta_curve.setData(np.array(time_data), np.array(beta_data))

# Timer to update the plot
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(500)  # Update interval in milliseconds

# Start the PyQtGraph application
if __name__ == '__main__':
    if not app.exec_():
        sys.exit(app.exec_())
