from exoplanet_loss.calculators.densidade_wind_stellar import rho_w
from exoplanet_loss.calculators.lx_age_calculator import LxAgeCalculator
from exoplanet_loss.calculators.photoevap_calculator import PhotoevaporationCalculator
from exoplanet_loss.calculators.stellar_wind_loss_calculator import calcular_perda_de_massa_interacao_vento_solar

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
    
    # Return results
    return {
        "lx": lx,
        "t_cor": t_cor,
        "mass_loss_photoev": mLossPhoto,
        "mass_loss_photoev_percent": mLossPhotoPercent,
        "mass_loss_wind": mLossWind,
        "mass_loss_wind_percent": mLossWindPercent,
        "total_mass_loss": totalMassLoss,
        "total_mass_loss_percent": totalMassLossPercent
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
    
    # Print results
    print(f"Luminosity: {results['lx']} erg/s")
    print(f"Coronal temperature: {results['t_cor']} K")
    print(f"Mass loss photoev: {results['mass_loss_photoev']} g")
    print(f"Mass loss photoev %: {results['mass_loss_photoev_percent']}%")
    print(f"Mass loss wind: {results['mass_loss_wind']} g")
    print(f"Mass loss wind %: {results['mass_loss_wind_percent']}%")
    print(f"Total mass loss: {results['total_mass_loss']} g")
    print(f"Total mass loss %: {results['total_mass_loss_percent']}%")

if __name__ == "__main__":
    main()