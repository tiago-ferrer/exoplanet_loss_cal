import math
import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from exoplanet_loss.utils.logging import get_logger

# Get logger for this module
logger = get_logger(__name__)


# Constants
AU = 1.496e11 * 100 # 1 AU in cm
kB = 1.380649e-23  # Boltzmann constant [J/K]
mp = 1.6726219e-27 * 1000  # proton mass [g]
G = 6.67430e-8  # gravitational constant [cm^3 g^-1 s^-2]


def generate_velocity_vs_distance_data(T_corona, Mstar, r_min=0.005, r_max=2.0, num_points=1000):
    """
    Generate data points for plotting stellar wind velocity vs distance.

    Parameters:
        T_corona (float): Coronal temperature [K]
        Mstar (float): Stellar mass [g]
        r_min (float): Minimum radius in AU
        r_max (float): Maximum radius in AU
        num_points (int): Number of data points to generate

    Returns:
        tuple: (distances, velocities) where:
            - distances is a list of distances in cm
            - velocities is a list of wind velocities in m/s
    """
    # Create array of distances in AU
    r_au = np.linspace(r_min, r_max, num_points)

    # Initial velocity guess
    v_initial_at_start = 5e6  # 5 km/s in cm/s

    # Calculate velocities at all radial distances
    v_sw_values = solve_solar_wind_velocity_tracking(r_au, T_corona, v_initial_at_start, Mstar)

    # Convert distances from AU to cm
    distances_cm = r_au * AU

    # Convert velocities from cm/s to m/s
    velocities_ms = v_sw_values / 100.0

    return distances_cm.tolist(), velocities_ms.tolist()



def calcular_perda_de_massa_interacao_vento_solar(R_p, Mstar, T_corona, eixo_maior, p_w):
    """
    Calculate mass loss due to solar wind interaction.

    Parameters:
        R_p : float - planet radius [cm]
        Mstar : float - stellar mass [g]
        T_corona : float - coronal temperature [K]
        eixo_maior : float - semi-major axis [AU]
        p_w : float - wind density [g/cm^3]

    Returns:
        float - mass loss rate [g/s]
    """
    u_w = get_interpolated_v_sw(Mstar, T_corona, eixo_maior)

    return 4 * math.pi * (R_p**2) * u_w * p_w

def parkers_equation(v, r, T, Mstar):
    """
    Parker's transcendental equation for solar wind velocity.

    Parameters:
        v : float - velocity to solve for [cm/s]
        r : float - radial distance [cm]
        T : float - coronal temperature [K]
        Mstar : float - stellar mass [M_sun] em gramas

    Returns:
        float - value of the equation to be zeroed
    """
    r_m = r * AU  # convert AU to cm
    cs2 = 2 * kB * T / mp  # square of sound speed

    # Calculate critical radius
    rc = G * Mstar / cs2

    # Ensure r_m is not exactly equal to rc to avoid log(1) in term2 derivation
    # and handle the v=cs singularity in term1 derivation more robustly
    # Note: fsolve needs the function to be continuous for the variable it solves for (v)

    # The equation to solve: v^2/cs^2 - log(v^2/cs2) = 4*log(r/rc) + 3
    # This form is v^2/cs^2 - log(v^2) + log(cs2) = 4*log(r) - 4*log(rc) + 3
    # Rearranging to be zeroed:
    # v^2/cs2 - log(v^2) + log(cs2) - 4*log(r) + 4*log(rc) - 3 = 0

    # Let's use the standard form for clarity in the return
    # v^2/cs^2 - log(v^2/cs^2) - (4*log(r/rc) + 3) = 0

    # To avoid potential issues with log(0) if v is near 0, add a small epsilon
    v_safe = np.maximum(v, 1e-10) # ensure velocity is non-negative for log

    term1 = (v_safe**2 / cs2) - np.log(v_safe**2 / cs2)
    term2 = 4 * np.log(r_m / rc) + 3

    return term1 - term2

def solve_solar_wind_velocity_tracking(r_vals, T, v_initial_at_start, Mstar):
    """
    Solve Parker's equation for a range of radial distances by tracking the solution.

    Parameters:
        r_vals : array-like - radial distances in AU. Should be sorted ascending.
        T : float - coronal temperature [K]
        v_initial_at_start : float - initial guess velocity [cm/s] at the first radial distance in r_vals
        Mstar : float - stellar mass [g], default is solar mass

    Returns:
        array - stellar wind velocities [cm/s] at each radial distance
    """
    v_vals = []

    # Use the provided initial velocity for the very first radial point
    current_v_guess = v_initial_at_start

    for r in r_vals:
        # Use the solution from the previous step as the initial guess for the current step
        # This helps track the correct physical branch
        try:
            # Solve the equation numerically using the previous solution as guess
            v_solution = fsolve(parkers_equation, current_v_guess, args=(r, T, Mstar), maxfev=5000, xtol=1e-9)[0]
            # Update the guess for the next iteration with the current solution
            current_v_guess = v_solution
            v_vals.append(v_solution)
        except Exception as e:
            # If fsolve fails to converge, append NaN or the last valid solution
            logger.warning(f"fsolve failed to converge at r = {r} AU with initial guess v = {current_v_guess:.2e} cm/s. Error: {e}")
            v_vals.append(np.nan) # Append NaN to indicate failure

    return np.array(v_vals)

def get_interpolated_v_sw(Mstar, T_corona, eixo_maior):
    """
    Given a critical radius (rc), returns the interpolated solar wind velocity (v_sw) at a target radius.

    Parameters:
        Mstar : float - stellar mass [g]
        T_corona : float - coronal temperature [K]
        eixo_maior : float - semi-major axis [AU]

    Returns:
        float - interpolated solar wind velocity [cm/s] at the target radius
    """

    r_start = 0.005 * AU # Starting distance in AU, needs to be small enough
    r_end = 2.0 * eixo_maior * AU  # Ending distance in AU
    num_points = 500  # Increase points for smoother tracking
    r_au = np.linspace(r_start, r_end, num_points)

    # Initial velocity guess
    v_initial_at_start = 5e6  # 5 km/s in cm/s

    # Calculate velocities at all radial distances
    v_sw_values = solve_solar_wind_velocity_tracking(r_au, T_corona, v_initial_at_start, Mstar)

    # Filter out any NaN values that might have occurred during solving
    valid_indices = ~np.isnan(v_sw_values)
    if np.sum(valid_indices) < 2:
        raise ValueError("Not enough valid velocity values for interpolation")

    v_sw_interp = interp1d(r_au[valid_indices], v_sw_values[valid_indices],
                          kind='linear', bounds_error=False, fill_value="extrapolate")

    # Return interpolated velocity at target radius
    return v_sw_interp(eixo_maior)
