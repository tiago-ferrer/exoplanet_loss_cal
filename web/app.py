import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify
from exoplanet_loss.data.exoplanet import get_exoplanet_data
from exoplanet_loss.calculador_final import calculate_mass_loss

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """Calculate mass loss based on form data."""
    try:
        # Get form data
        if request.form.get('use_api') == 'true':
            # Use API to get data
            star_name = request.form.get('star_name')
            planet_name = request.form.get('planet_name')

            # Get data from API
            data = get_exoplanet_data(star_name, planet_name)

            # Extract star and planet data
            star_data = {
                "Restrela": data["Restrela"],
                "Mestrela": data["Mestrela"],
                "t_gyr": data["t_gyr"]
            }

            planet_data = {
                "RplanetaEarth": data["RplanetaEarth"],
                "MplanetaEarth": data["MplanetaEarth"],
                "EixoMaiorPlaneta": data["EixoMaiorPlaneta"],
                "Excentricidade": data["Excentricidade"]
            }
        else:
            # Use manual input
            star_data = {
                "Restrela": float(request.form.get('stellar_radius')),
                "Mestrela": float(request.form.get('stellar_mass')),
                "t_gyr": float(request.form.get('stellar_age'))
            }

            planet_data = {
                "RplanetaEarth": float(request.form.get('planet_radius')),
                "MplanetaEarth": float(request.form.get('planet_mass')),
                "EixoMaiorPlaneta": float(request.form.get('semi_major_axis')),
                "Excentricidade": float(request.form.get('eccentricity'))
            }

        # Calculate mass loss
        results = calculate_mass_loss(star_data, planet_data)

        # Format results for display
        formatted_results = {
            "lx": f"{results['lx']:.2e} erg/s",
            "t_cor": f"{results['t_cor']:.2f} K",
            "mass_loss_photoev": f"{results['mass_loss_photoev']:.2e} g",
            "mass_loss_photoev_percent": f"{results['mass_loss_photoev_percent']:.2e}%",
            "mass_loss_wind": f"{results['mass_loss_wind']:.2e} g",
            "mass_loss_wind_percent": f"{results['mass_loss_wind_percent']:.2e}%",
            "total_mass_loss": f"{results['total_mass_loss']:.2e} g",
            "total_mass_loss_percent": f"{results['total_mass_loss_percent']:.2e}%"
        }

        return jsonify({"success": True, "results": formatted_results})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/exoplanet/<star_name>/<planet_name>')
def get_exoplanet(star_name, planet_name):
    """API endpoint to get exoplanet data."""
    try:
        data = get_exoplanet_data(star_name, planet_name)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
