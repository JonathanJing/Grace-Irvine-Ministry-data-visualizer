#!/bin/bash

# Ministry Data Visualizer - Streamlit App Runner
# Run this script from the project root directory

echo "Starting Ministry Data Visualizer..."
echo "Running from: $(pwd)"

# Check if we're in the right directory
if [ ! -f "app/ui.py" ]; then
    echo "Error: app/ui.py not found. Please run this script from the project root directory."
    exit 1
fi

# Activate virtual environment and run the Streamlit app
source .venv/bin/activate
python -m streamlit run app/ui.py
