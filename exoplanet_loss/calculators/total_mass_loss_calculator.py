import numpy as np
from scipy.integrate import simpson

from exoplanet_loss.calculators.lx_age_calculator import calculate_xray_luminosity, calculate_coronal_temperature_and_fx
from exoplanet_loss.calculators.stellar_wind_velocity_by_distance import generate_velocity_vs_distance_data
from exoplanet_loss.calculators.densidade_wind_stellar import rho_w
from exoplanet_loss.calculators.txc_mass_loss_stellar_wind import calcular_taxa_perda_de_massa_interacao_vento_solar
from exoplanet_loss.calculators.photoevap_calculator import calculo_perda_fotoevaporacao
from exoplanet_loss.utils.logging import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Constants
AU_TO_CM = 1.496e13  # 1 AU in cm
SOLAR_RADIUS_TO_CM = 6.957e10  # 1 solar radius in cm
SEC_PER_GYR = 3.1536e16  # seconds in 1 Gyr
G = 6.67430e-8  # gravitational constant [cm^3 g^-1 s^-2]

class TotalMassLossCalculator:
    def __init__(self, planet_radius_cm, planet_mass_g, planet_orbital_distance_au, 
                 eccentricity, stellar_radius_cm, stellar_mass_kg, 
                 efficiency_factor=0.3, min_age=0.01, max_age=None, age_step=0.1):
        """
        Initialize the total mass loss calculator with custom age steps.
        
        Parameters:
            planet_radius_cm (float): Planet radius in cm
            planet_mass_g (float): Planet mass in g
            planet_orbital_distance_au (float): Planet orbital distance in AU
            eccentricity (float): Orbital eccentricity
            stellar_radius_cm (float): Stellar radius in cm
            stellar_mass_kg (float): Stellar mass in kg
            efficiency_factor (float, optional): Efficiency factor for photoevaporation (0.25-1.0). Defaults to 0.3.
            min_age (float, optional): Minimum age in Gyr. Defaults to 0.01.
            max_age (float, optional): Maximum age in Gyr. If None, uses the default ages. Defaults to None.
            age_step (float, optional): Age step in Gyr. Defaults to 0.1.
        """
        self.planet_radius = planet_radius_cm
        self.planet_mass = planet_mass_g
        self.planet_orbital_distance_au = planet_orbital_distance_au
        self.planet_orbital_distance_cm = planet_orbital_distance_au * AU_TO_CM
        self.eccentricity = eccentricity
        self.stellar_radius = stellar_radius_cm
        self.stellar_mass = stellar_mass_kg
        self.efficiency_factor = efficiency_factor
        
        # Create custom age array
        if max_age is not None:
            self.ages = np.arange(min_age, max_age + age_step, age_step)
        else:
            # Use default ages if max_age is not provided
            self.ages = np.array([0.1, 0.3, 0.65, 1.6, 4.56, 6.7])
        
    def calculate_mass_loss(self):
        """
        Calculate the total mass loss due to both stellar wind and photoevaporation over time.
        
        Returns:
            tuple: (total_mass_loss, wind_mass_loss, photoevap_mass_loss, results_data)
                - total_mass_loss: Total integrated mass loss in g
                - wind_mass_loss: Total integrated mass loss due to stellar wind in g
                - photoevap_mass_loss: Total integrated mass loss due to photoevaporation in g
                - results_data: Dictionary containing detailed results for each age
        """
        # Arrays to store results for each age
        wind_mass_loss_rates = np.zeros_like(self.ages)
        photoevap_mass_loss_rates = np.zeros_like(self.ages)
        temperatures = np.zeros_like(self.ages)
        wind_velocities = np.zeros_like(self.ages)
        wind_densities = np.zeros_like(self.ages)
        x_ray_luminosities = np.zeros_like(self.ages)
        fx_values = np.zeros_like(self.ages)
        
        # Calculate parameters for each age
        for i, age in enumerate(self.ages):
            # 1. Calculate X-ray luminosity and coronal temperature
            lx = calculate_xray_luminosity(age)
            t_cor, fx = calculate_coronal_temperature_and_fx(lx, self.stellar_radius)
            temperatures[i] = t_cor
            x_ray_luminosities[i] = lx
            fx_values[i] = fx
            
            # 2. Solve Parker's equation for wind velocity
            # First convert planet distance from AU to solar radii for velocity calculation
            planet_distance_solar_radii = self.planet_orbital_distance_au * AU_TO_CM / SOLAR_RADIUS_TO_CM
            
            # Calculate wind velocity at planet's orbital distance
            _, _, velocity, _ = generate_velocity_vs_distance_data(
                T_corona=t_cor,
                r_planeta_au=self.planet_orbital_distance_au,
                r_min_au=0.1,  # Start close to the star
                r_max_au=self.planet_orbital_distance_au * 1.5,  # Go a bit beyond planet's orbit
                Mstar=self.stellar_mass,
                v_initial_at_start=5e3,  # Initial guess
                num_points=100
            )
            
            # Convert velocity from km/s to cm/s
            velocity_cm_s = velocity * 1e5
            wind_velocities[i] = velocity_cm_s
            
            # 3. Calculate wind density at planet's orbital distance
            density = rho_w(planet_distance_solar_radii, age)
            wind_densities[i] = density
            
            # 4. Calculate stellar wind mass loss rate
            wind_mass_loss_rate = calcular_taxa_perda_de_massa_interacao_vento_solar(
                self.planet_radius, density, velocity_cm_s
            )
            wind_mass_loss_rates[i] = wind_mass_loss_rate
            
            # 5. Calculate photoevaporation mass loss rate
            photoevap_mass_loss_rate = calculo_perda_fotoevaporacao(
                n=self.efficiency_factor,
                L_x=lx,
                R_p=self.planet_radius,
                G=G,
                M_p=self.planet_mass,
                a=self.planet_orbital_distance_cm,
                e=self.eccentricity
            )
            photoevap_mass_loss_rates[i] = photoevap_mass_loss_rate
        
        # 6. Integrate mass loss rates over time
        # Convert ages from Gyr to seconds for integration
        ages_seconds = self.ages * SEC_PER_GYR
        
        # Use Simpson's rule for integration
        wind_mass_loss = simpson(wind_mass_loss_rates, ages_seconds)
        photoevap_mass_loss = simpson(photoevap_mass_loss_rates, ages_seconds)
        total_mass_loss = wind_mass_loss + photoevap_mass_loss
        
        # Create results data dictionary
        results_data = {
            "ages": self.ages.tolist(),
            "x_ray_luminosities": x_ray_luminosities.tolist(),
            "fx_values": fx_values.tolist(),
            "temperatures": temperatures.tolist(),
            "wind_velocities": wind_velocities.tolist(),
            "wind_densities": wind_densities.tolist(),
            "wind_mass_loss_rates": wind_mass_loss_rates.tolist(),
            "photoevap_mass_loss_rates": photoevap_mass_loss_rates.tolist(),
            "total_mass_loss_rates": (wind_mass_loss_rates + photoevap_mass_loss_rates).tolist()
        }
        
        return total_mass_loss, wind_mass_loss, photoevap_mass_loss, results_data

def calculate_total_mass_loss(planet_radius_cm, planet_mass_g, planet_orbital_distance_au, 
                             eccentricity, stellar_radius_cm, stellar_mass_kg, 
                             efficiency_factor=0.3, min_age=0.01, max_age=None, age_step=0.1):
    """
    Convenience function to calculate total mass loss with custom age steps.
    
    Parameters:
        planet_radius_cm (float): Planet radius in cm
        planet_mass_g (float): Planet mass in g
        planet_orbital_distance_au (float): Planet orbital distance in AU
        eccentricity (float): Orbital eccentricity
        stellar_radius_cm (float): Stellar radius in cm
        stellar_mass_kg (float): Stellar mass in kg
        efficiency_factor (float, optional): Efficiency factor for photoevaporation (0.25-1.0). Defaults to 0.3.
        min_age (float, optional): Minimum age in Gyr. Defaults to 0.01.
        max_age (float, optional): Maximum age in Gyr. If None, uses the default ages. Defaults to None.
        age_step (float, optional): Age step in Gyr. Defaults to 0.1.
        
    Returns:
        tuple: (total_mass_loss, wind_mass_loss, photoevap_mass_loss, results_data)
    """
    calculator = TotalMassLossCalculator(
        planet_radius_cm, 
        planet_mass_g,
        planet_orbital_distance_au,
        eccentricity,
        stellar_radius_cm,
        stellar_mass_kg,
        efficiency_factor,
        min_age,
        max_age,
        age_step
    )
    
    return calculator.calculate_mass_loss()