#!/usr/bin/env python3
"""
Run script for the Exoplanet Loss web application.
This script provides an easy way to start the web application.
"""

import os
import sys
from web.app import app
from exoplanet_loss.utils.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)

def main():
    """Run the web application."""
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 10000))

    logger.info("Starting Exoplanet Loss web application...")
    logger.info(f"Server is running on all interfaces on port {port}")
    logger.info(f"For local access, open your browser and navigate to http://127.0.0.1:{port}/")
    logger.info("Press Ctrl+C to stop the server.")
    app.run(debug=False, host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped.")
        sys.exit(0)
