# Exoplanet Loss - Exoplanet Mass Loss Calculator

Exoplanet Loss is a Python package for calculating mass loss in exoplanets due to photoevaporation and stellar wind interaction. It includes tools for retrieving exoplanet data from online databases and performing detailed calculations of mass loss rates.

## Features

- Retrieve exoplanet data from NASA Exoplanet Archive and exoplanet.eu
- Calculate X-ray luminosity and coronal temperature based on stellar age
- Calculate mass loss due to photoevaporation
- Calculate mass loss due to stellar wind interaction
- Web interface for easy calculations

## Installation

### Using pip

```bash
pip install exoplanet_loss
```

### From source

```bash
git clone https://github.com/tiago-ferrer/exoplanet_loss.git
pip install -r requirements.txt
```

## Usage

### Command Line

```python
from exoplanet_loss.data.exoplanet import get_exoplanet_data
from exoplanet_loss.calculador_final import calculate_mass_loss

# Get data for Kepler 7b
data = get_exoplanet_data("Kepler", "7b")

# Extract star and planet data
star_data = {
    "Restrela": data["Restrela"],
    "Mestrela": data["Mestrela"],
    "t_gyr": data["t_gyr"]
}

planet_data = {
    "RplanetaEarth": data["RplanetaEarth"],
    "MplanetaEarth": data["MplanetaEarth"],
    "EixoMaiorPlaneta": data["EixoMaiorPlaneta"],
    "Excentricidade": data["Excentricidade"]
}

# Calculate mass loss
results = calculate_mass_loss(star_data, planet_data)

# Print results
print(f"Luminosity: {results['lx']} erg/s")
print(f"Coronal temperature: {results['t_cor']} K")
print(f"Mass loss photoev: {results['mass_loss_photoev']} g")
print(f"Mass loss photoev %: {results['mass_loss_photoev_percent']}%")
print(f"Mass loss wind: {results['mass_loss_wind']} g")
print(f"Mass loss wind %: {results['mass_loss_wind_percent']}%")
print(f"Total mass loss: {results['total_mass_loss']} g")
print(f"Total mass loss %: {results['total_mass_loss_percent']}%")
```

### Exoplanet Data Cache

The package includes a caching system for exoplanet data, which allows you to:
- Store exoplanet data locally to reduce API calls
- Add custom exoplanet data that might not be available in external databases
- Manage the cache by listing, removing, or clearing entries

#### Basic Cache Usage

```python
from exoplanet_loss.data.exoplanet import get_exoplanet_data

# First call will fetch from API and cache the data
data1 = get_exoplanet_data("Kepler", "7b")

# Second call will retrieve from cache (faster, works offline)
data2 = get_exoplanet_data("Kepler", "7b")
```

#### Adding Custom Data

```python
from exoplanet_loss.data.exoplanet import add_custom_exoplanet_data

# Define custom exoplanet data
custom_data = {
    "Restrela": 0.9,  # Solar radii
    "Mestrela": 0.8,  # Solar masses
    "RplanetaEarth": 2.5,  # Earth radii
    "MplanetaEarth": 10.0,  # Earth masses
    "EixoMaiorPlaneta": 0.1,  # AU
    "Excentricidade": 0.01,  # Eccentricity
    "t_gyr": 5.0  # Gyr
}

# Add to cache
add_custom_exoplanet_data("MyCustom", "Planet1", custom_data)

# Now you can retrieve it like any other exoplanet
data = get_exoplanet_data("MyCustom", "Planet1")
```

#### Managing the Cache

```python
from exoplanet_loss.data.exoplanet import (
    list_cached_exoplanets,
    remove_from_cache,
    clear_cache
)

# List all exoplanets in the cache
exoplanets = list_cached_exoplanets()
for exoplanet in exoplanets:
    print(f"- {exoplanet['full_name']}")

# Remove a specific exoplanet from the cache
removed = remove_from_cache("MyCustom", "Planet1")

# Clear the entire cache
clear_cache()
```

### Web Application

The package includes a web application that provides a user-friendly interface for performing calculations.

To run the web application:

```bash
# Option 1: Using the run_webapp.py script (recommended)
python run_webapp.py

# Option 2: Using Flask directly
cd web
flask run
```

Then open your browser and navigate to `http://127.0.0.1:10000/`.

### Deployment

The application is configured to be deployable on cloud platforms like render.com. It will:

- Listen on all network interfaces (0.0.0.0)
- Use the PORT environment variable if it's set, otherwise default to port 10000

To deploy on render.com:

1. Create a new Web Service
2. Connect your repository
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `python run_webapp.py`

## Package Structure

```
exoplanet_loss/
├── __init__.py
├── calculador_final.py
├── calculators/
│   ├── __init__.py
│   ├── densidade_wind_stellar.py
│   ├── lx_age_calculator.py
│   ├── photoevap_calculator.py
│   └── stellar_wind_loss_calculator.py
├── data/
│   ├── __init__.py
│   └── exoplanet.py
└── utils/
    └── __init__.py
```

## Dependencies

- numpy
- scipy
- matplotlib
- pandas
- requests
- pyvo (for accessing Virtual Observatory services)
- flask (for web application)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NASA Exoplanet Archive
- exoplanet.eu
