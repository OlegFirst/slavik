#!/bin/bash

# BCM JaamSim Runner Script
# Runs JaamSim simulations for BCM exercises

JAAMSIM_HOME=${JAAMSIM_HOME:-/opt/jaamsim}
SIMULATION_FILE=${1:-"$JAAMSIM_HOME/templates/bcm_default.cfg"}
OUTPUT_DIR=${2:-"$JAAMSIM_HOME/results"}

echo "Starting JaamSim simulation..."
echo "Simulation file: $SIMULATION_FILE"
echo "Output directory: $OUTPUT_DIR"

# Start virtual display if needed
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:99
    Xvfb :99 -screen 0 1280x1024x24 &
    XVFB_PID=$!
fi

# Run JaamSim simulation
java ${JAVA_OPTS:-"-Xmx2g"} -jar $JAAMSIM_HOME/JaamSim2023-03.jar -b $SIMULATION_FILE

# Clean up
if [ ! -z "$XVFB_PID" ]; then
    kill $XVFB_PID
fi

echo "Simulation completed. Results saved to: $OUTPUT_DIR"