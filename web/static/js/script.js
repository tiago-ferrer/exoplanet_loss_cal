// Store calculation results globally
let calculationResults = null;

$(document).ready(function() {
    // Handle manual form submission
    $('#manualForm').on('submit', function(e) {
        e.preventDefault();
        submitForm($(this));
    });

    // Handle API form submission
    $('#apiForm').on('submit', function(e) {
        e.preventDefault();
        submitForm($(this));
    });

    // Handle export velocity chart button click
    $('#exportVelocityBtn').on('click', function() {
        exportChart('velocity');
    });

    // Handle export density chart button click
    $('#exportDensityBtn').on('click', function() {
        exportChart('density');
    });

    // Function to submit form data
    function submitForm(form) {
        // Hide any previous results or errors
        $('#resultsCard').hide();
        $('#errorAlert').hide();

        // Show loading indicator
        const submitBtn = form.find('button[type="submit"]');
        const originalBtnText = submitBtn.text();
        submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Calculando...');

        // Submit form data via AJAX
        $.ajax({
            url: '/calculate',
            type: 'POST',
            data: form.serialize(),
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // Display results
                    displayResults(response.results);
                } else {
                    // Display error
                    $('#errorMessage').text(response.error);
                    $('#errorAlert').show();
                }
            },
            error: function(xhr, status, error) {
                // Display error
                $('#errorMessage').text('Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente.');
                $('#errorAlert').show();
            },
            complete: function() {
                // Reset button
                submitBtn.prop('disabled', false).text(originalBtnText);
            }
        });
    }

    // Function to display results
    function displayResults(results) {
        // Store results globally for use in export
        calculationResults = results;

        // Populate result fields
        $('#result_lx').text(results.lx);
        $('#result_t_cor').text(results.t_cor);
        $('#result_mass_loss_photoev').text(results.mass_loss_photoev);
        $('#result_mass_loss_photoev_percent').text(results.mass_loss_photoev_percent);
        $('#result_mass_loss_wind').text(results.mass_loss_wind);
        $('#result_mass_loss_wind_percent').text(results.mass_loss_wind_percent);
        $('#result_total_mass_loss').text(results.total_mass_loss);
        $('#result_total_mass_loss_percent').text(results.total_mass_loss_percent);
        $('#result_velocidade_vento_estelar').text(results.velicidade_vento_estelar);
        $('#result_densidade_vento_estelar').text(results.densidade_vento_estelar);
        $('#result_fator_de_eficiencia').text(results.fator_de_eficiencia);
        $('#result_idade_estrela').text(results.idade_estrela);

        // Create the density vs distance chart
        if (results.density_vs_distance) {
            createDensityDistanceChart(results.density_vs_distance, results.planet_distance);
        }

        // Create the velocity vs distance chart
        if (results.velocity_vs_distance) {
            createVelocityDistanceChart(results.velocity_vs_distance);
        }

        // Show results card
        $('#resultsCard').show();

        // Scroll to results
        $('html, body').animate({
            scrollTop: $('#resultsCard').offset().top - 20
        }, 500);
    }

    // Function to format numbers as "10ˣ" notation with superscript
    function formatPowerOfTen(value) {
        const exponent = Math.log10(Math.abs(value));

        // Return empty string if exponent has decimal part
        if (exponent % 1 !== 0) return '';

        // Map of digits to superscript equivalents
        const superscriptMap = {
            '0': '⁰',
            '1': '¹',
            '2': '²',
            '3': '³',
            '4': '⁴',
            '5': '⁵',
            '6': '⁶',
            '7': '⁷',
            '8': '⁸',
            '9': '⁹',
            '-': '⁻'
        };

        // Convert exponent to superscript
        const superscriptExponent = exponent.toString().split('').map(digit => superscriptMap[digit]).join('');

        return `10${superscriptExponent}`;
    }

    function formatPowerOfTenLinear(value) {
        const valueString = value.toExponential(0);

        // Split the string at 'e' to get parts before and after
        const parts = valueString.split('e');
        const beforeE = parts[0]; // Part before 'e'
        const afterE = parts[1];  // Part after 'e' (includes the sign)

        const superscriptMap = {
            '0': '⁰',
            '1': '¹',
            '2': '²',
            '3': '³',
            '4': '⁴',
            '5': '⁵',
            '6': '⁶',
            '7': '⁷',
            '8': '⁸',
            '9': '⁹',
            '-': '⁻',
            '+': ''

        };

        const superscriptExponent = afterE.toString().split('').map(digit => superscriptMap[digit]).join('');
        // Return the parts in the required format
        return `${beforeE} × 10${superscriptExponent}`;
    }

    // Function to create the density vs distance chart
    function createDensityDistanceChart(data, planet_distance) {
        const ctx = document.getElementById('densityDistanceChart').getContext('2d');

        // Configuration for major tick intervals (change these values to control the interval)
        const xAxisTickStep = 10; // Interval between major ticks on x-axis (in powers of 10)
        const yAxisTickStep = 10; // Interval between major ticks on y-axis (in powers of 10)

        // Destroy existing chart if it exists
        if (window.densityChart) {
            window.densityChart.destroy();
        }

        // Convert planet distance from AU to solar radii (1 AU = 215 Rsol)
        const planetDistanceRsol = planet_distance * 215;

        // Find the y-value (density) at the planet's distance
        let planetDensity = null;
        let closestIndex = 0;
        let minDistance = Number.MAX_VALUE;

        for (let i = 0; i < data.distances.length; i++) {
            const distance = Math.abs(data.distances[i] - planetDistanceRsol);
            if (distance < minDistance) {
                minDistance = distance;
                closestIndex = i;
                planetDensity = data.densities[i];
            }
        }

        // Create new chart
        window.densityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.distances,
                datasets: [{
                    label: 'Densidade (cm⁻³)',
                    data: data.densities,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                },
                {
                    // Add a point at the planet's distance
                    label: `Densidade na distância do planeta (${planetDistanceRsol.toExponential(2)} cm-3)`,
                    data: [{x: planetDistanceRsol, y: planetDensity}],
                    borderColor: 'rgba(255, 0, 0, 1)',
                    backgroundColor: 'rgba(255, 0, 0, 1)',
                    borderWidth: 2,
                    pointRadius: 5,
                    pointStyle: 'circle',
                    fill: false,
                    showLine: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'logarithmic',
                        title: {
                            display: true,
                            text: 'Distância (Rsol)'
                        },
                        ticks: {
                            callback: function(value, index, values) {
                                return formatPowerOfTen(value);
                            },
                            major: {
                                enabled: true
                            },
                            minor: {
                                enabled: false,
                                display: false
                            },
                            // Only show major ticks of log function (powers of 10)
                            filter: function(value, index, values) {
                                // Check if the value is a power of 10 (10^n where n is an integer)
                                return Math.log10(value) % 1 === 0;
                            }
                        }
                    },
                    y: {
                        type: 'logarithmic',
                        title: {
                            display: true,
                            text: 'Densidade (cm⁻³)'
                        },
                        ticks: {
                            callback: function(value, index, values) {
                                return formatPowerOfTen(value);
                            },
                            major: {
                                enabled: true
                            },
                            minor: {
                                enabled: false,
                                display: false
                            },
                            filter: function(value, index, values) {
                                return Math.log10(value) % 1 === 0;
                            }
                        }
                    }
                },
                annotation: {
                    annotations: {
                        line1: {
                            type: 'line',
                            xMin: planetDistanceRsol,
                            xMax: planetDistanceRsol,
                            borderColor: 'rgba(255, 0, 0, 0.5)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            label: {
                                content: `Distância do planeta: ${planetDistanceRsol.toExponential(2)} Rsol`,
                                enabled: true,
                                position: 'top'
                            }
                        },
                        line2: {
                            type: 'line',
                            yMin: planetDensity,
                            yMax: planetDensity,
                            borderColor: 'rgba(255, 0, 0, 0.5)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            label: {
                                content: `Densidade: ${planetDensity.toExponential(2)} cm⁻³`,
                                enabled: true,
                                position: 'left'
                            }
                        },
                        box1: {
                            type: 'box',
                            xMin: planetDistanceRsol * 0.9,
                            xMax: planetDistanceRsol * 1.1,
                            yMin: planetDensity * 0.9,
                            yMax: planetDensity * 1.1,
                            backgroundColor: 'rgba(255, 0, 0, 0.1)',
                            borderColor: 'rgba(255, 0, 0, 0.5)',
                            borderWidth: 1
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `Distância: ${context[0].parsed.x.toExponential(2)} Rsol`;
                            },
                            label: function(context) {
                                return `Densidade: ${context.parsed.y.toExponential(2)} cm⁻³`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Function to create the velocity vs distance chart
    function createVelocityDistanceChart(data) {
        const ctx = document.getElementById('velocityDistanceChart').getContext('2d');

        // Configuration for major tick intervals (change these values to control the interval)
        const xAxisTickStep = 10; // Interval between major ticks on x-axis (in powers of 10)
        const yAxisTickStep = 10; // Interval between major ticks on y-axis (in powers of 10)

        // Destroy existing chart if it exists
        if (window.velocityChart) {
            window.velocityChart.destroy();
        }

        // Create new chart
        window.velocityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.distances,
                datasets: [{
                    label: `Tcor = ${data.t_cor.toFixed(2)} K`,
                    data: data.velocities,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                },
                {
                    // Add a point at the planet's distance
                    label: `Velocidade na distância do planeta (${data.velocity.toExponential(2)} km/s)`,
                    data: [{x: data.distance, y: data.velocity}],
                    borderColor: 'rgba(255, 0, 0, 1)',
                    backgroundColor: 'rgba(255, 0, 0, 1)',
                    borderWidth: 2,
                    pointRadius: 5,
                    pointStyle: 'circle',
                    fill: false,
                    showLine: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Distância (au)'
                        },
                        ticks: {
                            beginAtZero: true,
                            callback: function(value, index, values) {
                                return value.toFixed(2);
                            },
                            major: {
                                enabled: true
                            },
                            minor: {
                                enabled: false,
                                display: false
                            }
                        }
                    },
                    y: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Velocidade do Vento Estelar(km/s)'
                        },
                        ticks: {
                            beginAtZero: true
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `Distância: ${context[0].parsed.x.toExponential(2)} au`;
                            },
                            label: function(context) {
                                return `Velocidade: ${context.parsed.y.toExponential(2)} km/s`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Function to export chart as PNG
    function exportChart(chartType) {
        let chart, title, xLabel, yLabel, planetDistance = null, planetValue = null;

        // Get the appropriate chart and its configuration
        if (chartType === 'velocity') {
            if (!window.velocityChart) {
                alert('Nenhum dado de gráfico disponível para exportar.');
                return;
            }
            chart = window.velocityChart;
            title = 'Velocidade do Vento Estelar vs Distância';
            xLabel = 'Distância (au)';
            yLabel = 'Velocidade do Vento Estelar (km/s)';

            // Get planet distance and velocity from the second dataset
            if (chart.data.datasets.length > 1 && chart.data.datasets[1].data.length > 0) {
                planetDistance = chart.data.datasets[1].data[0].x;
                planetValue = chart.data.datasets[1].data[0].y;
            }
        } else if (chartType === 'density') {
            if (!window.densityChart) {
                alert('Nenhum dado de gráfico disponível para exportar.');
                return;
            }
            chart = window.densityChart;
            title = 'Densidade vs Distância';
            xLabel = 'Distância (Rsol)';
            yLabel = 'Densidade (cm⁻³)';

            // Get planet distance and density from the second dataset
            if (chart.data.datasets.length > 1 && chart.data.datasets[1].data.length > 0) {
                planetDistance = chart.data.datasets[1].data[0].x;
                planetValue = chart.data.datasets[1].data[0].y;
            }
        } else {
            alert('Tipo de gráfico inválido.');
            return;
        }

        // Extract data from the chart
        const xData = chart.data.labels;
        const yData = chart.data.datasets[0].data;

        // Show loading indicator on the button
        const $btn = chartType === 'velocity' ? $('#exportVelocityBtn') : $('#exportDensityBtn');
        const originalBtnText = $btn.html();
        $btn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Exportando...');
        $btn.prop('disabled', true);

        // Send data to server for export
        fetch('/export_chart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chart_type: chartType,
                x_data: xData,
                y_data: yData,
                x_label: xLabel,
                y_label: yLabel,
                title: title,
                planet_distance: planetDistance,
                planet_value: planetValue,
                calculation_results: calculationResults // Include calculation results
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao exportar o gráfico');
            }
            return response.blob();
        })
        .then(blob => {
            // Create a download link and trigger it
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `${chartType}_chart.png`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);

            // Reset button
            $btn.html(originalBtnText);
            $btn.prop('disabled', false);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erro ao exportar o gráfico: ' + error.message);

            // Reset button
            $btn.html(originalBtnText);
            $btn.prop('disabled', false);
        });
    }
});
