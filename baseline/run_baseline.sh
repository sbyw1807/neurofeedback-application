#!/bin/bash

# Path to your Anaconda 'activate' script and your environment name
ANACONDA_ACTIVATE_SCRIPT="/opt/anaconda3/etc/profile.d/conda.sh"
ENV_NAME="neurofeedback"

# Activate Anaconda environment
source "$ANACONDA_ACTIVATE_SCRIPT"
conda activate "$ENV_NAME"

# Start Timeflux YAML script
timeflux -d /Users/Sophia/neurofeedback_baseline.yml &
PID_TIMEFLUX=$!

# Wait for a few seconds before starting other scripts
sleep 5

# Start real-time plotting Python script
python /Users/Sophia/realtime_plotting_markers.py &
PID_PLOT=$!

# Wait for the remaining time (total of 300 seconds - 5 minutes since Timeflux started)
# Adjust the sleep duration to 295 (300 - 5) seconds
sleep 295

# Stop all processes
kill $PID_TIMEFLUX $PID_PLOT

# Optionally deactivate the environment
conda deactivate

# chmod +x run_baseline.sh
# ./run_baseline.sh
