#!/bin/bash
# This script is used to start the Fortune Teller service.
CURRENT_DIR=$(pwd)
CONFIG_PATH="$CURRENT_DIR/config.yaml"
export PYTHONWARNINGS="ignore::RuntimeWarning"
clear

# Run Fortune Teller
PYTHONPATH="$CURRENT_DIR" python -m fortune_teller.main --config "$CONFIG_PATH"
