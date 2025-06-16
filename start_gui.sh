#!/bin/bash
# Linux/macOS shell script to start Starfish Python GUI

echo "Starting Starfish Python GUI..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python not found in PATH"
        echo "Please install Python 3.7 or higher"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Change to script directory
cd "$(dirname "$0")"

# Run the GUI
$PYTHON_CMD main.py "$@"

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "GUI exited with an error."
    read -p "Press Enter to close..."
fi
