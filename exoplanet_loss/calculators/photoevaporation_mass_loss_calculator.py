import numpy as np
from scipy.integrate import simpson

from exoplanet_loss.calculators.lx_age_calculator import calculate_xray_luminosity
from exoplanet_loss.calculators.photoevap_calculator import calculo_perda_fotoevaporacao
from exoplanet_loss.utils.logging import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Constants
G = 6.67430e-8  # gravitational constant [cm^3 g^-1 s^-2]
SEC_PER_GYR = 3.1536e16  # seconds in 1 Gyr

class PhotoevaporationMassLossCalculator:
    def __init__(self, planet_radius_cm, planet_mass_g, planet_orbital_distance_cm, eccentricity, efficiency_factor=0.3):
        """
        Initialize the photoevaporation mass loss calculator.
        
        Parameters:
            planet_radius_cm (float): Planet radius in cm
            planet_mass_g (float): Planet mass in g
            planet_orbital_distance_cm (float): Planet orbital distance in cm
            eccentricity (float): Orbital eccentricity
            efficiency_factor (float, optional): Efficiency factor for photoevaporation (0.25-1.0). Defaults to 0.3.
        """
        self.planet_radius = planet_radius_cm
        self.planet_mass = planet_mass_g
        self.planet_orbital_distance = planet_orbital_distance_cm
        self.eccentricity = eccentricity
        self.efficiency_factor = efficiency_factor
        
        # Pre-defined ages for integration (in Gyr)
        self.ages = np.array([0.1, 0.3, 0.65, 1.6, 4.56, 6.7])
        
    def calculate_mass_loss(self):
        """
        Calculate the total mass loss due to photoevaporation over time.
        
        Returns:
            tuple: (total_mass_loss, mass_loss_rates, x_ray_luminosities)
                - total_mass_loss: Total integrated mass loss in g
                - mass_loss_rates: Array of mass loss rates at each age in g/s
                - x_ray_luminosities: Array of X-ray luminosities at each age in erg/s
        """
        # Arrays to store results for each age
        mass_loss_rates = np.zeros_like(self.ages)
        x_ray_luminosities = np.zeros_like(self.ages)
        
        # Calculate parameters for each age
        for i, age in enumerate(self.ages):
            # Calculate X-ray luminosity for this age
            lx = calculate_xray_luminosity(age)
            x_ray_luminosities[i] = lx
            
            # Calculate mass loss rate due to photoevaporation
            mass_loss_rate = calculo_perda_fotoevaporacao(
                n=self.efficiency_factor,
                L_x=lx,
                R_p=self.planet_radius,
                G=G,
                M_p=self.planet_mass,
                a=self.planet_orbital_distance,
                e=self.eccentricity
            )
            mass_loss_rates[i] = mass_loss_rate
        
        # Integrate mass loss rate over time
        # Convert ages from Gyr to seconds for integration
        ages_seconds = self.ages * SEC_PER_GYR
        
        # Use Simpson's rule for integration
        total_mass_loss = simpson(mass_loss_rates, ages_seconds)
        
        return total_mass_loss, mass_loss_rates, x_ray_luminosities

def calculate_photoevaporation_mass_loss(planet_radius_cm, planet_mass_g, planet_orbital_distance_cm, 
                                        eccentricity, efficiency_factor=0.3):
    """
    Convenience function to calculate photoevaporation mass loss.
    
    Parameters:
        planet_radius_cm (float): Planet radius in cm
        planet_mass_g (float): Planet mass in g
        planet_orbital_distance_cm (float): Planet orbital distance in cm
        eccentricity (float): Orbital eccentricity
        efficiency_factor (float, optional): Efficiency factor for photoevaporation (0.25-1.0). Defaults to 0.3.
        
    Returns:
        float: Total mass loss in g
    """
    calculator = PhotoevaporationMassLossCalculator(
        planet_radius_cm, 
        planet_mass_g,
        planet_orbital_distance_cm,
        eccentricity,
        efficiency_factor
    )
    
    total_mass_loss, _, _ = calculator.calculate_mass_loss()
    return total_mass_loss

def main():
    """
    Example usage of the photoevaporation mass loss calculator.
    """
    # Example parameters (Earth-like planet)
    planet_radius_cm = 6.371e8  # Earth radius in cm
    planet_mass_g = 5.972e27  # Earth mass in g
    planet_orbital_distance_cm = 1.496e13  # 1 AU in cm
    eccentricity = 0.0167  # Earth's eccentricity
    efficiency_factor = 0.3  # Typical value
    
    # Create calculator
    calculator = PhotoevaporationMassLossCalculator(
        planet_radius_cm,
        planet_mass_g,
        planet_orbital_distance_cm,
        eccentricity,
        efficiency_factor
    )
    
    # Calculate mass loss
    total_mass_loss, mass_loss_rates, x_ray_luminosities = calculator.calculate_mass_loss()
    
    # Print results
    print(f"Ages (Gyr): {calculator.ages}")
    print(f"X-ray Luminosities (erg/s): {x_ray_luminosities}")
    print(f"Mass Loss Rates (g/s): {mass_loss_rates}")
    print(f"Total Mass Loss (g): {total_mass_loss}")
    
    # Convert to Earth masses for reference
    earth_mass_g = 5.972e27  # Earth mass in g
    total_mass_loss_earth_masses = total_mass_loss / earth_mass_g
    print(f"Total Mass Loss (Earth masses): {total_mass_loss_earth_masses}")

if __name__ == "__main__":
    main()