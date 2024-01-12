import time
import numpy as np
from pylsl import StreamInlet, resolve_stream
import h5py

# Resolve the alpha marker stream
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

# Initialize an array to store alpha values
alpha_values = []

# Calculate the time interval between samples based on the transmission rate
sample_interval = 1.0 / 2.0  # 2 Hz

# Run for a specified duration to capture baseline data
start_timestamp = time.time()
while time.time() - start_timestamp < 20:  # Adjust the duration as needed
    sample, timestamp = inlet.pull_sample(timeout=sample_interval) if inlet else (None, None)
    if sample:
        alpha_mean = sample[0]
        alpha_values.append(alpha_mean)
        print("Captured alpha value:", alpha_mean)

# Check if the alpha values are not empty before dividing into four equal ranges
if alpha_values:
    # Divide alpha values into four equal ranges
    bins = np.linspace(min(alpha_values), max(alpha_values), 5)

    # Calculate thresholds based on the ranges
    lower_threshold = bins[1]
    middle_lower_threshold = bins[2]
    middle_upper_threshold = bins[3]
    upper_threshold = bins[4]

    # Print the calculated thresholds
    print("Lower Threshold:", lower_threshold)
    print("Middle Lower Threshold:", middle_lower_threshold)
    print("Middle Upper Threshold:", middle_upper_threshold)
    print("Upper Threshold:", upper_threshold)

    # Generate a timestamp for the filename
    timestamp = time.strftime("%Y%m%d%H%M%S")
    
    # Save the thresholds to a text file with a timestamp in the filename
    file_path = f"/Users/Sophia/baseline_threshold_{timestamp}.txt"  # Adjust the file path as needed
    with open(file_path, "w") as txt_file:
        txt_file.write(f"Lower Threshold: {lower_threshold}\n")
        txt_file.write(f"Middle Lower Threshold: {middle_lower_threshold}\n")
        txt_file.write(f"Middle Upper Threshold: {middle_upper_threshold}\n")
        txt_file.write(f"Upper Threshold: {upper_threshold}\n")
else:
    print("No alpha values captured.")