#!/usr/bin/env python3
"""
Test script for the Exoplanet Loss package.
This script tests the main functionality of the package by calculating mass loss for Kepler 7b.
"""

from exoplanet_loss.data.exoplanet import get_exoplanet_data
from exoplanet_loss.calculador_final import calculate_mass_loss
from exoplanet_loss.utils.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)

def test_kepler_7b():
    """Test calculations for Kepler 7b."""
    logger.info("Testing calculations for Kepler 7b...")

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
    logger.info(f"Mass loss photoev %: {results['mass_loss_photoev_percent']:.6f}%")
    logger.info(f"Mass loss wind: {results['mass_loss_wind']:.2e} g")
    logger.info(f"Mass loss wind %: {results['mass_loss_wind_percent']:.6f}%")
    logger.info(f"Total mass loss: {results['total_mass_loss']:.2e} g")
    logger.info(f"Total mass loss %: {results['total_mass_loss_percent']:.6f}%")

    logger.info("Test completed successfully!")

if __name__ == "__main__":
    test_kepler_7b()
