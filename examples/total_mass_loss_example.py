import numpy as np
import matplotlib.pyplot as plt
from exoplanet_loss.calculators.stellar_wind_mass_loss_calculator import StellarWindMassLossCalculator
from exoplanet_loss.calculators.photoevaporation_mass_loss_calculator import PhotoevaporationMassLossCalculator

def main():
    """
    Example script demonstrating the calculation of total mass loss due to 
    both stellar wind and photoevaporation.
    
    This script:
    1. Creates calculator instances for both mechanisms
    2. Calculates mass loss for each mechanism
    3. Calculates total mass loss as the sum of both
    4. Plots the results
    """
    # Example parameters (Earth-like planet around a Sun-like star)
    planet_radius_cm = 6.371e8  # Earth radius in cm
    planet_mass_g = 5.972e27  # Earth mass in g
    planet_orbital_distance_au = 1.0  # 1 AU
    planet_orbital_distance_cm = 1.496e13  # 1 AU in cm
    eccentricity = 0.0167  # Earth's eccentricity
    efficiency_factor = 0.3  # Typical value for photoevaporation
    stellar_radius_cm = 6.957e10  # Solar radius in cm
    stellar_mass_kg = 1.989e30  # Solar mass in kg
    
    # Create stellar wind mass loss calculator
    wind_calculator = StellarWindMassLossCalculator(
        planet_radius_cm,
        planet_orbital_distance_au,
        stellar_radius_cm,
        stellar_mass_kg
    )
    
    # Create photoevaporation mass loss calculator
    photoevap_calculator = PhotoevaporationMassLossCalculator(
        planet_radius_cm,
        planet_mass_g,
        planet_orbital_distance_cm,
        eccentricity,
        efficiency_factor
    )
    
    # Calculate mass loss due to stellar wind
    wind_mass_loss, wind_rates, temperatures, wind_velocities, wind_densities = wind_calculator.calculate_mass_loss()
    
    # Calculate mass loss due to photoevaporation
    photoevap_mass_loss, photoevap_rates, x_ray_luminosities = photoevap_calculator.calculate_mass_loss()
    
    # Calculate total mass loss
    total_mass_loss = wind_mass_loss + photoevap_mass_loss
    
    # Print results
    print("Total Mass Loss Calculator Results")
    print("=================================")
    print(f"Planet radius: {planet_radius_cm:.2e} cm")
    print(f"Planet mass: {planet_mass_g:.2e} g")
    print(f"Planet orbital distance: {planet_orbital_distance_au:.2f} AU")
    print(f"Stellar radius: {stellar_radius_cm:.2e} cm")
    print(f"Stellar mass: {stellar_mass_kg:.2e} kg")
    print("\nResults:")
    print(f"Ages (Gyr): {wind_calculator.ages}")
    
    print("\nStellar Wind Mass Loss:")
    print(f"Mass Loss Rates (g/s): {wind_rates}")
    print(f"Total Mass Loss (g): {wind_mass_loss}")
    print(f"Percentage of Total: {(wind_mass_loss/total_mass_loss)*100:.2f}%")
    
    print("\nPhotoevaporation Mass Loss:")
    print(f"Mass Loss Rates (g/s): {photoevap_rates}")
    print(f"Total Mass Loss (g): {photoevap_mass_loss}")
    print(f"Percentage of Total: {(photoevap_mass_loss/total_mass_loss)*100:.2f}%")
    
    print("\nTotal Mass Loss:")
    print(f"Total Mass Loss (g): {total_mass_loss}")
    
    # Convert to Earth masses for reference
    earth_mass_g = 5.972e27  # Earth mass in g
    total_mass_loss_earth_masses = total_mass_loss / earth_mass_g
    wind_mass_loss_earth_masses = wind_mass_loss / earth_mass_g
    photoevap_mass_loss_earth_masses = photoevap_mass_loss / earth_mass_g
    
    print(f"Total Mass Loss (Earth masses): {total_mass_loss_earth_masses}")
    print(f"Wind Mass Loss (Earth masses): {wind_mass_loss_earth_masses}")
    print(f"Photoevaporation Mass Loss (Earth masses): {photoevap_mass_loss_earth_masses}")
    
    # Create plots
    create_plots(
        wind_calculator.ages, 
        wind_rates, 
        photoevap_rates, 
        wind_mass_loss, 
        photoevap_mass_loss, 
        total_mass_loss
    )

def create_plots(ages, wind_rates, photoevap_rates, wind_mass_loss, photoevap_mass_loss, total_mass_loss):
    """
    Create plots of the results.
    
    Parameters:
        ages (array): Ages in Gyr
        wind_rates (array): Stellar wind mass loss rates in g/s
        photoevap_rates (array): Photoevaporation mass loss rates in g/s
        wind_mass_loss (float): Total stellar wind mass loss in g
        photoevap_mass_loss (float): Total photoevaporation mass loss in g
        total_mass_loss (float): Total mass loss in g
    """
    # Create figure with 2 subplots
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Total Mass Loss Analysis', fontsize=16)
    
    # Plot 1: Mass Loss Rates vs Age
    axs[0].plot(ages, wind_rates, 'o-', color='blue', label='Stellar Wind')
    axs[0].plot(ages, photoevap_rates, 'o-', color='red', label='Photoevaporation')
    axs[0].plot(ages, wind_rates + photoevap_rates, 'o-', color='purple', label='Total')
    axs[0].set_xlabel('Age (Gyr)')
    axs[0].set_ylabel('Mass Loss Rate (g/s)')
    axs[0].set_title('Mass Loss Rates vs Age')
    axs[0].set_yscale('log')
    axs[0].grid(True)
    axs[0].legend()
    
    # Plot 2: Pie chart of total mass loss contributions
    labels = ['Stellar Wind', 'Photoevaporation']
    sizes = [wind_mass_loss, photoevap_mass_loss]
    colors = ['blue', 'red']
    explode = (0.1, 0.1)  # explode both slices
    
    axs[1].pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    axs[1].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    axs[1].set_title('Contribution to Total Mass Loss')
    
    # Add text with total mass loss
    earth_mass_g = 5.972e27  # Earth mass in g
    total_mass_loss_earth_masses = total_mass_loss / earth_mass_g
    axs[1].text(0, -1.2, f'Total Mass Loss: {total_mass_loss:.2e} g\n({total_mass_loss_earth_masses:.2e} Earth masses)', 
             horizontalalignment='center', fontsize=10)
    
    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust for suptitle
    plt.savefig('total_mass_loss.png')
    plt.show()

if __name__ == "__main__":
    main()