import requests
import json

# Base URL for the API
base_url = "http://localhost:5000"

def test_api_error():
    """Test error message from the API endpoint."""
    # Use a non-existent planet to trigger an error
    response = requests.get(f"{base_url}/api/exoplanet/NonExistentStar/NonExistentPlanet")
    data = response.json()
    
    print("API Error Test:")
    print(f"Success: {data['success']}")
    print(f"Error Message: {data['error']}")
    print()
    
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
    
    print("Calculate Error Test:")
    print(f"Success: {data['success']}")
    print(f"Error Message: {data['error']}")
    print()
    
    # Verify that the error message is in Portuguese
    assert "Não foi possível encontrar dados" in data['error'], "Error message not in Portuguese"

if __name__ == "__main__":
    print("Testing error messages in Portuguese...")
    print("Make sure the web application is running on http://localhost:5000")
    print()
    
    try:
        test_api_error()
        test_calculate_error()
        print("All tests passed! Error messages are in Portuguese.")
    except AssertionError as e:
        print(f"Test failed: {str(e)}")
    except Exception as e:
        print(f"Error running tests: {str(e)}")