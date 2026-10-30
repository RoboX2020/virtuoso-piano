#!/bin/bash
# Launch the air piano (sets up the python environment and runs main.py).
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run setup first."
    exit 1
fi

# Run the app
python3 main.py
