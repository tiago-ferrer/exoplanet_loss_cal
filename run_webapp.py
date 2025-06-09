#!/usr/bin/env python3
"""
Run script for the Exoplanet Loss web application.
This script provides an easy way to start the web application.
"""

import os
import sys
from web.app import app

def main():
    """Run the web application."""
    print("Starting Exoplanet Loss web application...")
    print("Open your browser and navigate to http://127.0.0.1:5000/")
    print("Press Ctrl+C to stop the server.")
    app.run(debug=True)

if __name__ == "__main__":
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
