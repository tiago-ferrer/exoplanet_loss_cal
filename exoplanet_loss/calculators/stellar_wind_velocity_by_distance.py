import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import fsolve

from exoplanet_loss.utils.logging import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Constants
AU = 1.496e11  # 1 AU in meters
kB = 1.380649e-23  # Boltzmann constant [J/K]
mp = 1.6726219e-27  # proton mass [kg]
G = 6.67430e-11  # gravitational constant [m^3 kg^-1 s^-2]
AU_km = 1.496e8  # 1 AU in meters

def generate_velocity_vs_distance_data(T_corona, r_planeta_au, r_min_au, r_max_au, Mstar, v_initial_at_start=5e3, num_points=500, max_attempts=10):
    """
    Generate data points for plotting stellar wind velocity vs distance.
    Ensures that the velocity data always has an ascending trend from 0 to 0.1 AU.
    If a decreasing trend is detected, the initial velocity guess is increased and the calculation is repeated.

    Parameters:
        T_corona (float): Coronal temperature [K]
        r_min (float): Minimum radius in AU
        r_max (float): Maximum radius in AU
        r_planeta(float): raio do planeta in AU
        Mstar(float): number in kg
        v_initial_at_start (float, optional): Initial guess velocity [m/s] at the first radial distance. Defaults to 5e3 m/s.
        num_points (int): Number of data points to generate
        max_attempts (int, optional): Maximum number of attempts to achieve ascending trend. Defaults to 10.

    Returns:
        tuple: (distances, velocities, velocity, final_initial_velocity) where:
            - distances is a list of distances in au
            - velocities is a list of wind velocities in km/s
            - velocity in km/s
            - final_initial_velocity is the final initial velocity value used after adjustments
    """
    # Create array of distances in cm
    r_au = np.linspace(r_min_au, r_max_au, num_points)

    # Initial velocity guess
    current_v_initial = v_initial_at_start

    # Flag to track if we have an ascending trend
    ascending_trend = False
    attempts = 0

    while not ascending_trend and attempts < max_attempts:
        # Calculate velocities at all radial distances
        v_sw_values = solve_solar_wind_velocity_tracking(r_au, T_corona, Mstar, current_v_initial)

        # Check if velocity has ascending trend from 0 to 0.1 AU
        # Find indices of points between 0 and 0.1 AU
        near_star_indices = np.where((r_au >= 0) & (r_au <= 0.1))[0]

        if len(near_star_indices) >= 2:
            # Get velocities for these points
            near_star_velocities = v_sw_values[near_star_indices]

            # Check if trend is ascending (each value >= previous value)
            is_ascending = all(near_star_velocities[i] >= near_star_velocities[i-1] 
                              for i in range(1, len(near_star_velocities)))

            if is_ascending:
                ascending_trend = True
                logger.info(f"Ascending velocity trend achieved with initial velocity {current_v_initial} m/s")
            else:
                # Increase initial velocity guess by 50%
                current_v_initial *= 1.5
                logger.info(f"Detected decreasing velocity trend. Increasing initial velocity to {current_v_initial} m/s")
        else:
            # Not enough points to check trend, assume it's fine
            ascending_trend = True

        attempts += 1

    if not ascending_trend:
        logger.warning(f"Could not achieve ascending velocity trend after {max_attempts} attempts")

    interpolation_function = interp1d(r_au, v_sw_values, kind='linear', fill_value="extrapolate")
    veloc = float(interpolation_function(r_planeta_au))

    return r_au.tolist(), v_sw_values.tolist(), veloc, current_v_initial


def parkers_equation(v, r, T, Mstar):
    """
    Parker's transcendental equation for solar wind velocity.

    Parameters:
        v : float - velocity to solve for [m/s]
        r : float - radial distance [AU]
        T : float - coronal temperature [K]
        Mstar : float - stellar mass [kg]

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
    v_safe = np.maximum(v, 1e-10)  # ensure velocity is non-negative for log

    term1 = (v_safe ** 2 / cs2) - np.log(v_safe ** 2 / cs2)
    term2 = 4 * np.log(r_m / rc) + 3

    return term1 - term2


def solve_solar_wind_velocity_tracking(r_vals, T,Mstar, v_initial_at_start):
    """
    Solve Parker's equation for a range of radial distances by tracking the solution.

    Parameters:
        r_vals : array-like - radial distances [AU]. Should be sorted ascending.
        T : float - coronal temperature [K]
        v_initial_at_start : float - initial guess velocity [m/s] at the first radial distance in r_vals
        Mstar : massa da estrela em kg

    Returns:
        array - solar wind velocities [m/s] at each radial distance
    """
    cs = np.sqrt(2 * kB * T / mp)  # sound speed
    v_vals = []

    # Use the provided initial velocity for the very first radial point
    current_v_guess = v_initial_at_start

    for r in r_vals:
        # Use the solution from the previous step as the initial guess for the current step
        # This helps track the correct physical branch
        try:
            # Solve the equation numerically using the previous solution as guess
            v_solution = fsolve(parkers_equation, current_v_guess, args=(r, T,Mstar), maxfev=5000, xtol=1e-9)[0]
            # Update the guess for the next iteration with the current solution
            current_v_guess = v_solution
            v_vals.append(v_solution)
        except Exception as e:
            # If fsolve fails to converge, append NaN or the last valid solution
            logger.warning(
                f"Warning: fsolve failed to converge at r = {r} AU with initial guess v = {current_v_guess:.2e} m/s. Error: {e}")
            v_vals.append(np.nan)  # Append NaN to indicate failure

    return np.array(v_vals)