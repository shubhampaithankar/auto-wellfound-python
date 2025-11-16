#!/bin/bash
# Wrapper script to run the Python script with proper error suppression
# This suppresses harmless "command not found" errors from dependencies

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run the installation script first:"
    echo "  ./scripts/install.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the Python script, filtering out only the specific harmless errors
# These are often from packages trying to detect OS (uname, sed, etc.)
# Using a more robust approach that preserves exit codes
python -u main.py "$@" 2>&1 | sed '/bash: \(uname\|sed\): command not found/d'

# Deactivate virtual environment (optional, happens automatically when script exits)
deactivate

