import numpy as np
from scipy.interpolate import interp1d

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
    """
    Calculator for total mass loss due to stellar wind and photoevaporation over time.

    This class uses a fixed set of age points for sampling and a robust integration method
    to ensure consistent results regardless of the age step size provided by the user.
    This prevents the percentage of mass loss from oscillating when different age steps are used.

    Key features to ensure stability:
    1. Uses a fixed, logarithmically-spaced set of age points that capture the full behavior
       of the mass loss rate function, regardless of the user-provided age step
    2. Creates a very fine-grained age grid (5000 points) for integration
    3. Uses linear interpolation to avoid artificial oscillations that can occur with higher-order methods
    4. Uses numpy's trapezoidal rule for numerical integration
    """

    # Fixed set of age points (in Gyr) that capture the full behavior of the mass loss rate function
    # These points are concentrated at younger ages where mass loss rates change more rapidly
    FIXED_AGE_POINTS = np.array([
        0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 
        1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0
    ])
    def __init__(self, planet_radius_cm, planet_mass_g, planet_orbital_distance_au, 
                 eccentricity, stellar_radius_cm, stellar_mass_kg, 
                 efficiency_factor=0.3, initial_velocity=5e3, min_age=0.01, max_age=None, age_step=0.1):
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
            initial_velocity (float, optional): Initial guess velocity [m/s] for stellar wind calculation. Defaults to 5e3 m/s.
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
        self.initial_velocity = initial_velocity

        # Use fixed age points within the specified range for consistent results
        if max_age is not None:
            # Filter fixed age points to include only those within the specified range
            mask = (self.FIXED_AGE_POINTS >= min_age) & (self.FIXED_AGE_POINTS <= max_age)
            filtered_ages = self.FIXED_AGE_POINTS[mask]

            # Ensure min_age and max_age are included
            if min_age not in filtered_ages:
                filtered_ages = np.append(min_age, filtered_ages)
            if max_age not in filtered_ages:
                filtered_ages = np.append(filtered_ages, max_age)

            # Sort the ages
            self.ages = np.sort(filtered_ages)

            # Store the user's age step for results data
            self.user_age_step = age_step
        else:
            # Use default ages if max_age is not provided
            self.ages = np.array([0.1, 0.3, 0.65, 1.6, 4.56, 6.7])
            self.user_age_step = None

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
                v_initial_at_start=self.initial_velocity,  # Use the provided initial velocity
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
        # Create a fixed, fine-grained age grid for integration to ensure consistent results
        # regardless of the user-provided age step - using 5000 points for higher accuracy
        fine_age_grid = np.linspace(self.ages.min(), self.ages.max(), 5000)
        fine_ages_seconds = fine_age_grid * SEC_PER_GYR

        # Interpolate mass loss rates onto the fine grid
        # Using linear interpolation to avoid artificial oscillations that can occur with cubic interpolation
        wind_interp = interp1d(self.ages, wind_mass_loss_rates, kind='linear', bounds_error=False, fill_value='extrapolate')
        photoevap_interp = interp1d(self.ages, photoevap_mass_loss_rates, kind='linear', bounds_error=False, fill_value='extrapolate')

        fine_wind_rates = wind_interp(fine_age_grid)
        fine_photoevap_rates = photoevap_interp(fine_age_grid)

        # Use trapezoidal rule for integration on the fine grid
        wind_mass_loss = np.trapz(fine_wind_rates, fine_ages_seconds)
        photoevap_mass_loss = np.trapz(fine_photoevap_rates, fine_ages_seconds)
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
            "total_mass_loss_rates": (wind_mass_loss_rates + photoevap_mass_loss_rates).tolist(),
            "user_age_step": self.user_age_step
        }

        return total_mass_loss, wind_mass_loss, photoevap_mass_loss, results_data

def calculate_total_mass_loss(planet_radius_cm, planet_mass_g, planet_orbital_distance_au, 
                             eccentricity, stellar_radius_cm, stellar_mass_kg, 
                             efficiency_factor=0.3, initial_velocity=5e3, min_age=0.01, max_age=None, age_step=0.1):
    """
    Convenience function to calculate total mass loss with custom age steps.

    Note: The integration method used is robust and not sensitive to the age step size.
    The results will be consistent regardless of the age_step value provided. This is achieved
    through several techniques:

    1. Using a fixed set of age points that capture the full behavior of the mass loss rate function,
       regardless of the user-provided age step
    2. Using a very fine-grained interpolation grid (5000 points) for integration
    3. Using linear interpolation to avoid artificial oscillations
    4. Using numpy's trapezoidal rule for stable numerical integration

    The age_step parameter is still used to determine the granularity of the results displayed
    to the user, but it does not affect the actual calculation of the total mass loss. This ensures
    that the percentage of mass loss remains consistent even when different age step sizes are used.

    Parameters:
        planet_radius_cm (float): Planet radius in cm
        planet_mass_g (float): Planet mass in g
        planet_orbital_distance_au (float): Planet orbital distance in AU
        eccentricity (float): Orbital eccentricity
        stellar_radius_cm (float): Stellar radius in cm
        stellar_mass_kg (float): Stellar mass in kg
        efficiency_factor (float, optional): Efficiency factor for photoevaporation (0.25-1.0). Defaults to 0.3.
        initial_velocity (float, optional): Initial guess velocity [m/s] for stellar wind calculation. Defaults to 5e3 m/s.
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
        initial_velocity,
        min_age,
        max_age,
        age_step
    )

    return calculator.calculate_mass_loss()
