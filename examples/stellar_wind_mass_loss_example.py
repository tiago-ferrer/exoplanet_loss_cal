import numpy as np
import matplotlib.pyplot as plt
from exoplanet_loss.calculators.stellar_wind_mass_loss_calculator import StellarWindMassLossCalculator

def main():
    """
    Example script demonstrating the use of the StellarWindMassLossCalculator.
    
    This script:
    1. Creates a StellarWindMassLossCalculator instance
    2. Calculates mass loss due to stellar wind over time
    3. Plots the results
    """
    # Example parameters (Earth-like planet around a Sun-like star)
    planet_radius_cm = 6.371e8  # Earth radius in cm
    planet_orbital_distance_au = 1.0  # 1 AU
    stellar_radius_cm = 6.957e10  # Solar radius in cm
    stellar_mass_kg = 1.989e30  # Solar mass in kg
    
    # Create calculator
    calculator = StellarWindMassLossCalculator(
        planet_radius_cm,
        planet_orbital_distance_au,
        stellar_radius_cm,
        stellar_mass_kg
    )
    
    # Calculate mass loss
    total_mass_loss, mass_loss_rates, temperatures, velocities, densities = calculator.calculate_mass_loss()
    
    # Print results
    print("Stellar Wind Mass Loss Calculator Results")
    print("=========================================")
    print(f"Planet radius: {planet_radius_cm:.2e} cm")
    print(f"Planet orbital distance: {planet_orbital_distance_au:.2f} AU")
    print(f"Stellar radius: {stellar_radius_cm:.2e} cm")
    print(f"Stellar mass: {stellar_mass_kg:.2e} kg")
    print("\nResults:")
    print(f"Ages (Gyr): {calculator.ages}")
    print(f"Coronal Temperatures (K): {temperatures}")
    print(f"Wind Velocities (cm/s): {velocities}")
    print(f"Wind Densities (g/cm³): {densities}")
    print(f"Mass Loss Rates (g/s): {mass_loss_rates}")
    print(f"Total Mass Loss (g): {total_mass_loss}")
    
    # Convert to Earth masses for reference
    earth_mass_g = 5.972e27  # Earth mass in g
    total_mass_loss_earth_masses = total_mass_loss / earth_mass_g
    print(f"Total Mass Loss (Earth masses): {total_mass_loss_earth_masses}")
    
    # Create plots
    create_plots(calculator.ages, mass_loss_rates, temperatures, velocities, densities)

def create_plots(ages, mass_loss_rates, temperatures, velocities, densities):
    """
    Create plots of the results.
    
    Parameters:
        ages (array): Ages in Gyr
        mass_loss_rates (array): Mass loss rates in g/s
        temperatures (array): Coronal temperatures in K
        velocities (array): Wind velocities in cm/s
        densities (array): Wind densities in g/cm³
    """
    # Create figure with 2x2 subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Stellar Wind Mass Loss Analysis', fontsize=16)
    
    # Plot 1: Coronal Temperature vs Age
    axs[0, 0].plot(ages, temperatures, 'o-', color='red')
    axs[0, 0].set_xlabel('Age (Gyr)')
    axs[0, 0].set_ylabel('Coronal Temperature (K)')
    axs[0, 0].set_title('Coronal Temperature vs Age')
    axs[0, 0].grid(True)
    
    # Plot 2: Wind Velocity vs Age
    axs[0, 1].plot(ages, velocities/1e5, 'o-', color='blue')  # Convert to km/s
    axs[0, 1].set_xlabel('Age (Gyr)')
    axs[0, 1].set_ylabel('Wind Velocity (km/s)')
    axs[0, 1].set_title('Wind Velocity vs Age')
    axs[0, 1].grid(True)
    
    # Plot 3: Wind Density vs Age
    axs[1, 0].plot(ages, densities, 'o-', color='green')
    axs[1, 0].set_xlabel('Age (Gyr)')
    axs[1, 0].set_ylabel('Wind Density (g/cm³)')
    axs[1, 0].set_title('Wind Density vs Age')
    axs[1, 0].grid(True)
    
    # Plot 4: Mass Loss Rate vs Age
    axs[1, 1].plot(ages, mass_loss_rates, 'o-', color='purple')
    axs[1, 1].set_xlabel('Age (Gyr)')
    axs[1, 1].set_ylabel('Mass Loss Rate (g/s)')
    axs[1, 1].set_title('Mass Loss Rate vs Age')
    axs[1, 1].grid(True)
    
    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust for suptitle
    plt.savefig('stellar_wind_mass_loss.png')
    plt.show()

if __name__ == "__main__":
    main()