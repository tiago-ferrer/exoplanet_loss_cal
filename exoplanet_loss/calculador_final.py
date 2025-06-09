from exoplanet_loss.calculators.densidade_wind_stellar import rho_w, generate_density_vs_distance_data
from exoplanet_loss.calculators.lx_age_calculator import LxAgeCalculator
from exoplanet_loss.calculators.photoevap_calculator import PhotoevaporationCalculator
from exoplanet_loss.calculators.stellar_wind_loss_calculator import calcular_perda_de_massa_interacao_vento_solar, generate_velocity_vs_distance_data
from exoplanet_loss.utils.logging import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Constants
Rsun = 6.957e10  # cm
Msun = 1.98e31  # grams
Rearth = 6.371e8  # cm
Mearth = 5.97e27  # grams
AU = 1.496e11 * 100  # 1 AU in cm

def calculate_mass_loss(star_data, planet_data):
    """
    Calculate mass loss for a planet due to photoevaporation and stellar wind.

    Parameters:
        star_data (dict): Dictionary containing stellar properties
            - Restrela: Stellar radius in solar radii
            - Mestrela: Stellar mass in solar masses
            - t_gyr: Age of the system in Gyr
        planet_data (dict): Dictionary containing planet properties
            - RplanetaEarth: Planet radius in Earth radii
            - MplanetaEarth: Planet mass in Earth masses
            - EixoMaiorPlaneta: Semi-major axis in AU
            - Excentricidade: Orbital eccentricity

    Returns:
        dict: Dictionary containing mass loss results
            - lx: X-ray luminosity in erg/s
            - t_cor: Coronal temperature in K
            - mass_loss_photoev: Mass loss due to photoevaporation in g
            - mass_loss_photoev_percent: Mass loss due to photoevaporation as percentage of planet mass
            - mass_loss_wind: Mass loss due to stellar wind in g
            - mass_loss_wind_percent: Mass loss due to stellar wind as percentage of planet mass
            - total_mass_loss: Total mass loss in g
            - total_mass_loss_percent: Total mass loss as percentage of planet mass
    """
    # Extract data
    Restrela = star_data["Restrela"]  # Solar radii
    Mestrela = star_data["Mestrela"]  # Solar masses
    t_gyr = star_data["t_gyr"]  # Gyr

    RplanetaEarth = planet_data["RplanetaEarth"]  # Earth radii
    MplanetaEarth = planet_data["MplanetaEarth"]  # Earth masses
    EixoMaiorPlaneta = planet_data["EixoMaiorPlaneta"]  # AU
    Excentricidade = planet_data["Excentricidade"]  # Eccentricity

    # Calculate X-ray luminosity and coronal temperature
    lx_age = LxAgeCalculator(t_gyr, Restrela * Rsun)
    lx, t_cor = lx_age.getLx(), lx_age.getTCor()

    # Calculate mass loss due to photoevaporation
    photoEvp = PhotoevaporationCalculator(0.3, lx, RplanetaEarth * Rearth, MplanetaEarth * Mearth, 
                                         EixoMaiorPlaneta * AU, Excentricidade)
    mLossPhoto = photoEvp.get()
    mLossPhotoPercent = (mLossPhoto * 100) / (MplanetaEarth * Mearth)

    # Calculate mass loss due to stellar wind
    d_w = rho_w(Restrela * Rsun, t_gyr)
    mLossWind = calcular_perda_de_massa_interacao_vento_solar(RplanetaEarth * Rearth, Mestrela * Msun, 
                                                             t_cor, EixoMaiorPlaneta, d_w)
    mLossWindPercent = (mLossWind * 100) / (MplanetaEarth * Mearth)

    # Calculate total mass loss
    totalMassLoss = mLossWind + mLossPhoto
    totalMassLossPercent = ((mLossWind + mLossPhoto) * 100) / (MplanetaEarth * Mearth)

    # Generate density vs distance data for plotting
    # Convert AU to solar radii (1 AU = 215 Rsun)
    r_min_solar = 0.005 * AU /Rsun  # Convert from AU to solar radii
    r_max_solar = 2 * AU /Rsun     # Convert from AU to solar radii
    distances, densities = generate_density_vs_distance_data(r_min=r_min_solar, r_max=r_max_solar, num_points=1000)

    # Generate velocity vs distance data for plotting
    r_min_au = 0.005  # Minimum radius in AU
    r_max_au = 2.0    # Maximum radius in AU
    vel_distances, velocities = generate_velocity_vs_distance_data(T_corona=t_cor, Mstar=Mestrela * Msun,
                                                                 r_min=r_min_au*1e-5, r_max=(EixoMaiorPlaneta*AU*1.20)*1e-5, num_points=1000)

    # Return results
    return {
        "lx": lx,
        "t_cor": t_cor,
        "mass_loss_photoev": mLossPhoto,
        "mass_loss_photoev_percent": mLossPhotoPercent,
        "mass_loss_wind": mLossWind,
        "mass_loss_wind_percent": mLossWindPercent,
        "total_mass_loss": totalMassLoss,
        "total_mass_loss_percent": totalMassLossPercent,
        "density_vs_distance": {
            "distances": distances,
            "densities": densities
        },
        "velocity_vs_distance": {
            "t_cor": t_cor,
            "distances": vel_distances,
            "velocities": velocities
        }
    }

def main():
    """
    Example usage of the calculate_mass_loss function with Kepler 7b data.
    """
    # Kepler 7b data
    star_data = {
        "Restrela": 1.78,  # Solar radii
        "Mestrela": 1.41,  # Solar masses
        "t_gyr": 3.5  # Gyr
    }

    planet_data = {
        "RplanetaEarth": 18.18,  # Earth radii
        "MplanetaEarth": 140,  # Earth masses
        "EixoMaiorPlaneta": 0.06067,  # AU
        "Excentricidade": 0.026  # Eccentricity
    }

    results = calculate_mass_loss(star_data, planet_data)

    # Log results
    logger.info(f"Luminosity: {results['lx']} erg/s")
    logger.info(f"Coronal temperature: {results['t_cor']} K")
    logger.info(f"Mass loss photoev: {results['mass_loss_photoev']} g")
    logger.info(f"Mass loss photoev %: {results['mass_loss_photoev_percent']}%")
    logger.info(f"Mass loss wind: {results['mass_loss_wind']} g")
    logger.info(f"Mass loss wind %: {results['mass_loss_wind_percent']}%")
    logger.info(f"Total mass loss: {results['total_mass_loss']} g")
    logger.info(f"Total mass loss %: {results['total_mass_loss_percent']}%")

if __name__ == "__main__":
    main()
