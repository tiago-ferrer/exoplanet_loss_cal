import numpy as np

# Constants from the fit in Lx_versus_age.ipynb
A_FIT = 6.76e27  # Coefficient A in the power-law fit
B_FIT = -1.92    # Exponent b in the power-law fit
class LxAgeCalculator:
    def __init__(self, age, raio_estrela):
        self.age = age
        self.raio_estrela = raio_estrela

    def getLx(self):
        return calculate_xray_luminosity(self.age)
    def getTCor(self):
        return calculate_coronal_temperature(self.getLx(),self.raio_estrela)


def calculate_xray_luminosity(age_gyr):
    """
    Calcula a luminosidade de raios X com base na idade estelar.

    Parâmetros:
    -----------
    age_gyr : float ou array-like
    Idade estelar em Giga-anos (Gyr)

    Retorna:
    --------
    float ou array-like
    Luminosidade de raios X em erg/s

    Observações:
    ------
    Usa a relação de lei de potência: Lx = A * age^b
    onde A = 6,76e27 e b = -1,92

    Esta relação é derivada de dados de Ribas et al. (2005)
    para a banda de raios X de 1-20 Å.
    """
    return A_FIT * np.power(age_gyr, B_FIT)

def calculate_coronal_temperature(lx, radius):
    """
    Calculate coronal temperature based on X-ray luminosity and stellar radius.
    
    Parameters:
    -----------
    lx : float or array-like
        X-ray luminosity in erg/s
    radius_solar : float or array-like, optional
        Stellar radius in solar radii, default is 1.0 (solar radius)
    
    Returns:
    --------
    float or array-like
        Coronal temperature in Kelvin
    
    Notes:
    ------
    First calculates the X-ray flux at the stellar surface:
        Fx = Lx / (4 * π * R_star^2)
    Then calculates the coronal temperature:
        T_cor = 0.11 * Fx^0.26 * 1e6
    """
    
    # Calculate X-ray flux at stellar surface
    fx = lx / (4.0 * np.pi * radius**2)
    
    # Calculate coronal temperature
    t_cor = 0.11 * np.power(fx, 0.26) * 1e6
    
    return t_cor

def plot_lx_vs_age(age_min=0.1, age_max=10.0, num_points=100):
    """
    Plot X-ray luminosity vs. stellar age.
    
    Parameters:
    -----------
    age_min : float, optional
        Minimum age in Gyr, default is 0.1
    age_max : float, optional
        Maximum age in Gyr, default is 10.0
    num_points : int, optional
        Number of points to plot, default is 100
    
    Returns:
    --------
    tuple
        (fig, ax) matplotlib figure and axis objects
    """
    import matplotlib.pyplot as plt
    
    # Generate age values
    ages = np.linspace(age_min, age_max, num_points)
    
    # Calculate corresponding X-ray luminosities
    lx_values = calculate_xray_luminosity(ages)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ages, lx_values)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Age (Gyr)')
    ax.set_ylabel('X-ray Luminosity (erg/s)')
    ax.set_title('X-ray Luminosity vs. Stellar Age')
    ax.grid(True, which="both", ls="--")
    
    return fig, ax

def get_lx_Tcor(age):
    lx = calculate_xray_luminosity(age)
    t_cor = calculate_coronal_temperature(lx)
    return lx, t_cor