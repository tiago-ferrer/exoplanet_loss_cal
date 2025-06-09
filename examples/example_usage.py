#!/usr/bin/env python3
"""
Example usage of the Exoplanet Loss package.
This script demonstrates how to use the package to calculate mass loss for exoplanets.
"""

from exoplanet_loss.data.exoplanet import get_exoplanet_data
from exoplanet_loss.calculador_final import calculate_mass_loss
from exoplanet_loss.utils.logging import configure_logging, get_logger
import matplotlib.pyplot as plt
import numpy as np

# Configure logging
configure_logging()
logger = get_logger(__name__)

def example_kepler_7b():
    """Example calculation for Kepler 7b."""
    logger.info("Example calculation for Kepler 7b:")

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

    # Log results
    logger.info("Results:")
    logger.info(f"Luminosity: {results['lx']:.2e} erg/s")
    logger.info(f"Coronal temperature: {results['t_cor']:.2f} K")
    logger.info(f"Mass loss photoev: {results['mass_loss_photoev']:.2e} g")
    logger.info(f"Mass loss photoev %: {results['mass_loss_photoev_percent']:.2e}%")
    logger.info(f"Mass loss wind: {results['mass_loss_wind']:.2e} g")
    logger.info(f"Mass loss wind %: {results['mass_loss_wind_percent']:.2e}%")
    logger.info(f"Total mass loss: {results['total_mass_loss']:.2e} g")
    logger.info(f"Total mass loss %: {results['total_mass_loss_percent']:.2e}%")

def example_custom_planet():
    """Example calculation for a custom planet."""
    logger.info("Example calculation for a custom planet:")

    # Define star data
    star_data = {
        "Restrela": 1.0,  # Solar radii
        "Mestrela": 1.0,  # Solar masses
        "t_gyr": 4.5  # Gyr
    }

    # Define planet data
    planet_data = {
        "RplanetaEarth": 1.0,  # Earth radii
        "MplanetaEarth": 1.0,  # Earth masses
        "EixoMaiorPlaneta": 1.0,  # AU
        "Excentricidade": 0.0  # Eccentricity
    }

    # Calculate mass loss
    results = calculate_mass_loss(star_data, planet_data)

    # Log results
    logger.info("Results:")
    logger.info(f"Luminosity: {results['lx']:.2e} erg/s")
    logger.info(f"Coronal temperature: {results['t_cor']:.2f} K")
    logger.info(f"Mass loss photoev: {results['mass_loss_photoev']:.2e} g")
    logger.info(f"Mass loss photoev %: {results['mass_loss_photoev_percent']:.6f}%")
    logger.info(f"Mass loss wind: {results['mass_loss_wind']:.2e} g")
    logger.info(f"Mass loss wind %: {results['mass_loss_wind_percent']:.6f}%")
    logger.info(f"Total mass loss: {results['total_mass_loss']:.2e} g")
    logger.info(f"Total mass loss %: {results['total_mass_loss_percent']:.6f}%")

def example_plot_mass_loss_vs_distance():
    """Example plot of mass loss vs. distance."""
    logger.info("Generating plot of mass loss vs. distance...")

    # Define star data
    star_data = {
        "Restrela": 1.0,  # Solar radii
        "Mestrela": 1.0,  # Solar masses
        "t_gyr": 4.5  # Gyr
    }

    # Define planet data template
    planet_data_template = {
        "RplanetaEarth": 1.0,  # Earth radii
        "MplanetaEarth": 1.0,  # Earth masses
        "Excentricidade": 0.0  # Eccentricity
    }

    # Define distances to calculate
    distances = np.linspace(0.1, 2.0, 20)  # AU

    # Calculate mass loss at each distance
    photoev_loss = []
    wind_loss = []
    total_loss = []

    for distance in distances:
        planet_data = planet_data_template.copy()
        planet_data["EixoMaiorPlaneta"] = distance

        results = calculate_mass_loss(star_data, planet_data)

        photoev_loss.append(results["mass_loss_photoev_percent"])
        wind_loss.append(results["mass_loss_wind_percent"])
        total_loss.append(results["total_mass_loss_percent"])

    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(distances, photoev_loss, 'b-', label='Photoevaporation')
    plt.plot(distances, wind_loss, 'r-', label='Stellar Wind')
    plt.plot(distances, total_loss, 'g-', label='Total')

    plt.xlabel('Distance (AU)')
    plt.ylabel('Mass Loss (%)')
    plt.title('Mass Loss vs. Distance')
    plt.legend()
    plt.grid(True)

    plt.savefig('mass_loss_vs_distance.png')
    logger.info("Plot saved as 'mass_loss_vs_distance.png'")

if __name__ == "__main__":
    example_kepler_7b()
    example_custom_planet()
    example_plot_mass_loss_vs_distance()
