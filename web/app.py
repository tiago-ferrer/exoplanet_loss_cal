import os
import sys
import re
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify, Response
from exoplanet_loss.data.exoplanet import get_exoplanet_data
from exoplanet_loss.calculador_final import calculate_mass_loss

# Dictionary of common error messages and their Portuguese translations
ERROR_TRANSLATIONS = {
    # Exoplanet data errors
    "Error connecting to exoplanet database": "Erro ao conectar ao banco de dados de exoplanetas",

    # Input validation errors
    "missing required key": "faltando chave obrigatória",
    "is not a valid number": "não é um número válido",
    "must be a positive number": "deve ser um número positivo",

    # Generic errors
    "An unexpected error occurred": "Ocorreu um erro inesperado",
    "Invalid input": "Entrada inválida",
    "Calculation error": "Erro de cálculo"
}

def translate_error(error_message):
    """
    Translate error messages from English to Portuguese.

    Args:
        error_message (str): The original error message in English

    Returns:
        str: The translated error message in Portuguese
    """
    # Check for exact matches first
    if error_message in ERROR_TRANSLATIONS:
        return ERROR_TRANSLATIONS[error_message]

    # Check for partial matches
    for eng, port in ERROR_TRANSLATIONS.items():
        if eng in error_message:
            # Replace the English part with the Portuguese translation
            return error_message.replace(eng, port)

    # If no match is found, return a generic error message
    return "Ocorreu um erro: " + error_message

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
            "total_mass_loss_percent": f"{results['total_mass_loss_percent']:.2e}%",
            "planet_distance": planet_data["EixoMaiorPlaneta"],  # Pass the planet's distance for reference lines
            "density_vs_distance": results['density_vs_distance'],  # Pass the density vs distance data for plotting
            "velocity_vs_distance": results['velocity_vs_distance']  # Pass the velocity vs distance data for plotting
        }

        return jsonify({"success": True, "results": formatted_results})

    except Exception as e:
        return jsonify({"success": False, "error": translate_error(str(e))})

@app.route('/api/exoplanet/<star_name>/<planet_name>')
def get_exoplanet(star_name, planet_name):
    """API endpoint to get exoplanet data."""
    try:
        data = get_exoplanet_data(star_name, planet_name)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": translate_error(str(e))})

@app.route('/export_chart', methods=['POST'])
def export_chart():
    """Export chart data as PNG using matplotlib."""
    try:
        # Get chart data from request
        data = request.json
        chart_type = data.get('chart_type')
        x_data = data.get('x_data', [])
        y_data = data.get('y_data', [])
        x_label = data.get('x_label', '')
        y_label = data.get('y_label', '')
        title = data.get('title', '')
        planet_distance = data.get('planet_distance')
        planet_value = data.get('planet_value')
        calculation_results = data.get('calculation_results', {})

        # Create figure with specified size (8,4)
        plt.figure(figsize=(8, 4))

        # Create plot based on chart type
        if chart_type == 'density':
            # Logarithmic scale for density chart
            plt.loglog(x_data, y_data)
            plt.grid(True, which="both", ls="-")

            # Add point at planet's distance if available
            if planet_distance is not None and planet_value is not None:
                plt.scatter([planet_distance], [planet_value], color='red', s=50, zorder=5)
                # Add text annotation for the value
                plt.annotate(f"Densidade: {planet_value:.2e} cm⁻³", 
                             xy=(planet_distance, planet_value),
                             xytext=(10, 10), textcoords='offset points',
                             color='red', fontsize=9,
                             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8))

        elif chart_type == 'velocity':
            # Linear scale for velocity chart
            plt.plot(x_data, y_data)
            plt.grid(True)

            # Add point at planet's distance if available
            if planet_distance is not None and planet_value is not None:
                plt.scatter([planet_distance], [planet_value], color='red', s=50, zorder=5)
                # Add text annotation for the value
                plt.annotate(f"Velocidade: {planet_value:.2e} m/s", 
                             xy=(planet_distance, planet_value),
                             xytext=(10, 10), textcoords='offset points',
                             color='red', fontsize=9,
                             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8))

        # Add labels and title
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)

        # Adjust layout first
        plt.tight_layout()

        # Save plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()

        # Return the image as a response
        return Response(buf.getvalue(), mimetype='image/png')

    except Exception as e:
        return jsonify({"success": False, "error": translate_error(str(e))}), 400

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
