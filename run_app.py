#!/usr/bin/env python3
"""
Entry point for the Ministry Data Visualizer Streamlit app.
Run this script from the project root directory.
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Get the path to the app/ui.py file
    app_path = Path(__file__).parent / "app" / "ui.py"
    
    # Get the path to the virtual environment python
    venv_python = Path(__file__).parent / ".venv" / "bin" / "python"
    
    # Use virtual environment python if it exists, otherwise use system python
    if venv_python.exists():
        python_executable = str(venv_python)
    else:
        python_executable = sys.executable
    
    # Run streamlit with the app
    cmd = [python_executable, "-m", "streamlit", "run", str(app_path)]
    
    print(f"Starting Streamlit app from: {app_path}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nApp stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error running app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
