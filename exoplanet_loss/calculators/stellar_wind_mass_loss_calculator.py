import numpy as np
from scipy.integrate import simpson

from exoplanet_loss.calculators.lx_age_calculator import calculate_xray_luminosity, calculate_coronal_temperature_and_fx
from exoplanet_loss.calculators.stellar_wind_velocity_by_distance import generate_velocity_vs_distance_data
from exoplanet_loss.calculators.densidade_wind_stellar import rho_w
from exoplanet_loss.calculators.txc_mass_loss_stellar_wind import calcular_taxa_perda_de_massa_interacao_vento_solar
from exoplanet_loss.utils.logging import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Constants
AU_TO_CM = 1.496e13  # 1 AU in cm
SOLAR_RADIUS_TO_CM = 6.957e10  # 1 solar radius in cm
SEC_PER_GYR = 3.1536e16  # seconds in 1 Gyr

class StellarWindMassLossCalculator:
    def __init__(self, planet_radius_cm, planet_orbital_distance_au, stellar_radius_cm, stellar_mass_kg):
        """
        Initialize the stellar wind mass loss calculator.
        
        Parameters:
            planet_radius_cm (float): Planet radius in cm
            planet_orbital_distance_au (float): Planet orbital distance in AU
            stellar_radius_cm (float): Stellar radius in cm
            stellar_mass_kg (float): Stellar mass in kg
        """
        self.planet_radius = planet_radius_cm
        self.planet_orbital_distance = planet_orbital_distance_au
        self.stellar_radius = stellar_radius_cm
        self.stellar_mass = stellar_mass_kg
        
        # Pre-defined ages for integration (in Gyr)
        self.ages = np.array([0.1, 0.3, 0.65, 1.6, 4.56, 6.7])
        
    def calculate_mass_loss(self):
        """
        Calculate the total mass loss due to stellar wind over time.
        
        Returns:
            tuple: (total_mass_loss, mass_loss_rates, temperatures, velocities, densities)
                - total_mass_loss: Total integrated mass loss in g
                - mass_loss_rates: Array of mass loss rates at each age in g/s
                - temperatures: Array of coronal temperatures at each age in K
                - velocities: Array of wind velocities at each age in cm/s
                - densities: Array of wind densities at each age in g/cm³
        """
        # Arrays to store results for each age
        mass_loss_rates = np.zeros_like(self.ages)
        temperatures = np.zeros_like(self.ages)
        velocities = np.zeros_like(self.ages)
        densities = np.zeros_like(self.ages)
        
        # Calculate parameters for each age
        for i, age in enumerate(self.ages):
            # 1. Calculate X-ray luminosity and coronal temperature
            lx = calculate_xray_luminosity(age)
            t_cor, fx = calculate_coronal_temperature_and_fx(lx, self.stellar_radius)
            temperatures[i] = t_cor
            
            # 2. Solve Parker's equation for wind velocity
            # First convert planet distance from AU to solar radii for velocity calculation
            planet_distance_solar_radii = self.planet_orbital_distance * AU_TO_CM / SOLAR_RADIUS_TO_CM
            
            # Calculate wind velocity at planet's orbital distance
            _, _, velocity = generate_velocity_vs_distance_data(
                T_corona=t_cor,
                r_planeta_au=self.planet_orbital_distance,
                r_min_au=0.1,  # Start close to the star
                r_max_au=self.planet_orbital_distance * 1.5,  # Go a bit beyond planet's orbit
                Mstar=self.stellar_mass,
                v_initial_at_start=5e3,  # Initial guess
                num_points=100
            )
            
            # Convert velocity from km/s to cm/s
            velocity_cm_s = velocity * 1e5
            velocities[i] = velocity_cm_s
            
            # 3. Calculate wind density at planet's orbital distance
            density = rho_w(planet_distance_solar_radii, age)
            densities[i] = density
            
            # 4. Calculate mass loss rate
            mass_loss_rate = calcular_taxa_perda_de_massa_interacao_vento_solar(
                self.planet_radius, density, velocity_cm_s
            )
            mass_loss_rates[i] = mass_loss_rate
        
        # 5. Integrate mass loss rate over time
        # Convert ages from Gyr to seconds for integration
        ages_seconds = self.ages * SEC_PER_GYR
        
        # Use Simpson's rule for integration
        total_mass_loss = simpson(mass_loss_rates, ages_seconds)
        
        return total_mass_loss, mass_loss_rates, temperatures, velocities, densities

def calculate_stellar_wind_mass_loss(planet_radius_cm, planet_orbital_distance_au, 
                                    stellar_radius_cm, stellar_mass_kg):
    """
    Convenience function to calculate stellar wind mass loss.
    
    Parameters:
        planet_radius_cm (float): Planet radius in cm
        planet_orbital_distance_au (float): Planet orbital distance in AU
        stellar_radius_cm (float): Stellar radius in cm
        stellar_mass_kg (float): Stellar mass in kg
        
    Returns:
        float: Total mass loss in g
    """
    calculator = StellarWindMassLossCalculator(
        planet_radius_cm, 
        planet_orbital_distance_au,
        stellar_radius_cm,
        stellar_mass_kg
    )
    
    total_mass_loss, _, _, _, _ = calculator.calculate_mass_loss()
    return total_mass_loss

def main():
    """
    Example usage of the stellar wind mass loss calculator.
    """
    # Example parameters

    planet_radius_cm = 1.992 * 637800000 # Earth radius in cm
    planet_orbital_distance_au = 0.0618  # 1 AU
    stellar_radius_cm = 0.949 * 6.9634e10  # Solar radius in cm
    stellar_mass_kg = 0.956 * 1.989e30  # Solar mass in kg
    
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

if __name__ == "__main__":
    main()