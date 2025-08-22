#!/bin/bash

# Ministry Data Visualizer - Setup Script
# This script activates the virtual environment and installs requirements

echo "Setting up Ministry Data Visualizer..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo "Setup complete! You can now run the app with:"
echo "  ./run_app.sh"
echo "  or"
echo "  python run_app.py"
