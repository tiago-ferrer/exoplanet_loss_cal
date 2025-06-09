#!/usr/bin/env python3
"""
Test script for the Exoplanet Loss package.
This script tests the main functionality of the package by calculating mass loss for Kepler 7b.
"""

from exoplanet_loss.data.exoplanet import get_exoplanet_data
from exoplanet_loss.calculador_final import calculate_mass_loss

def test_kepler_7b():
    """Test calculations for Kepler 7b."""
    print("Testing calculations for Kepler 7b...")

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
    print("\nResults:")
    print(f"Luminosity: {results['lx']:.2e} erg/s")
    print(f"Coronal temperature: {results['t_cor']:.2f} K")
    print(f"Mass loss photoev: {results['mass_loss_photoev']:.2e} g")
    print(f"Mass loss photoev %: {results['mass_loss_photoev_percent']:.6f}%")
    print(f"Mass loss wind: {results['mass_loss_wind']:.2e} g")
    print(f"Mass loss wind %: {results['mass_loss_wind_percent']:.6f}%")
    print(f"Total mass loss: {results['total_mass_loss']:.2e} g")
    print(f"Total mass loss %: {results['total_mass_loss_percent']:.6f}%")

    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_kepler_7b()
