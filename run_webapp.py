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
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 10000))

    print("Starting Exoplanet Loss web application...")
    print(f"Server is running on all interfaces on port {port}")
    print(f"For local access, open your browser and navigate to http://127.0.0.1:{port}/")
    print("Press Ctrl+C to stop the server.")
    app.run(debug=False, host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
