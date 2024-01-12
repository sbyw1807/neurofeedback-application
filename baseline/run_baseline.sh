#!/bin/bash

# Initialize conda
source /opt/anaconda3/etc/profile.d/conda.sh || exit 1  # Adjust the path as needed

# Activate conda environment
conda activate neurofeedback || exit 1  # Exit if activation fails

# Path to your Python environment (replace with your actual path)
PYTHON_EXECUTABLE="/opt/anaconda3/envs/neurofeedback/bin/python"

# Function to run the entire process with a timeout
run_neurofeedback() {
    gtimeout 30s bash -c '
        # Run timeflux graph in the background
        timeflux -d /Users/Sophia/neurofeedback_baseline.yml &
        TIMEFLUX_PID=$!

        # Sleep for a few seconds to allow timeflux to initialize
        sleep 5

        # Run the baseline measurement script in the background
        $0 /Users/Sophia/baseline_measurement.py &

        # Run the plotting script in the background
        $0 /Users/Sophia/realtime_plotting_marker.py &

        # Wait for all background processes to finish
        wait $TIMEFLUX_PID
    ' "$PYTHON_EXECUTABLE"
}

# Run the entire process with a timeout
run_neurofeedback

# chmod +x run_baseline.sh
# ./run_baseline.sh