import numpy as np

# Constants
Ns = 2.6e7  # Number density at the source in cm^-3
m_H = 1.67e-24  # Proton mass in g


def n_r(r):
    """
    Calculate the number density of the stellar wind as a function of radius.

    This function implements a model with three components that vary with different 
    powers of the radius.

    Parameters:
        r (float): Radius in solar radii

    Returns:
        float: Number density at radius r in cm^-3
    """
    return 7e4 * r**(-1.67) + 4.1e6 * r**(-4) + Ns * r**(-6)


def rho_w(r, t_gyr):
    """
    Calculate the mass density of the stellar wind as a function of radius and stellar age.

    The density scales with stellar age according to a power law with exponent -0.3.

    Parameters:
        r (float): Radius in cm
        t_gyr (float): Stellar age in Gyr

    Returns:
        float: Mass density at radius r and age t_gyr in g/cm³
    """
    n = n_r(r)
    factor_age = (4.56 / t_gyr)**0.3  # Age scaling factor (normalized to solar age)
    return n * (m_H / 2) * factor_age  # Convert number density to mass density in g/cm³