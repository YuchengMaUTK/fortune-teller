#!/bin/bash
# Start services script for Fortune Teller with streaming enabled
# Sets up environment and starts the application in streaming mode

#!/bin/bash
# This script is used to start the Fortune Teller service.
CURRENT_DIR=$(pwd)
CONFIG_PATH="$CURRENT_DIR/config.yaml"
export PYTHONWARNINGS="ignore::RuntimeWarning"
clear

# Set environment variables for streaming
export FORTUNE_TELLER_STREAMING=true
export FORTUNE_TELLER_LOG_LEVEL=DEBUG

# Function to run with streaming mode
run_with_streaming() {
  # Run the application
  python -m fortune_teller.main
}

# Process command line arguments
case "$1" in
  *)
    run_with_streaming
    ;;
esac

exit 0