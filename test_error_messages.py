import requests
import json
from exoplanet_loss.utils.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Base URL for the API
base_url = "http://localhost:10000"

def test_api_error():
    """Test error message from the API endpoint."""
    # Use a non-existent planet to trigger an error
    response = requests.get(f"{base_url}/api/exoplanet/NonExistentStar/NonExistentPlanet")
    data = response.json()

    logger.info("API Error Test:")
    logger.info(f"Success: {data['success']}")
    logger.info(f"Error Message: {data['error']}")

    # Verify that the error message is in Portuguese
    assert "Não foi possível encontrar dados" in data['error'], "Error message not in Portuguese"

def test_calculate_error():
    """Test error message from the calculate endpoint."""
    # Send invalid data to trigger an error
    invalid_data = {
        "use_api": "true",
        "star_name": "NonExistentStar",
        "planet_name": "NonExistentPlanet"
    }

    response = requests.post(f"{base_url}/calculate", data=invalid_data)
    data = response.json()

    logger.info("Calculate Error Test:")
    logger.info(f"Success: {data['success']}")
    logger.info(f"Error Message: {data['error']}")

    # Verify that the error message is in Portuguese
    assert "Não foi possível encontrar dados" in data['error'], "Error message not in Portuguese"

if __name__ == "__main__":
    logger.info("Testing error messages in Portuguese...")
    logger.info("Make sure the web application is running on http://localhost:10000")

    try:
        test_api_error()
        test_calculate_error()
        logger.info("All tests passed! Error messages are in Portuguese.")
    except AssertionError as e:
        logger.error(f"Test failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
