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

Then open your browser and navigate to `http://127.0.0.1:5000/`.

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
- flask (for web application)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NASA Exoplanet Archive
- exoplanet.eu
