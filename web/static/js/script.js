// Store calculation results globally
let calculationResults = null;

$(document).ready(function () {
    // Handle manual form submission
    $('#manualForm').on('submit', function (e) {
        e.preventDefault();
        submitForm($(this));
    });

    // Handle API form submission
    $('#apiForm').on('submit', function (e) {
        e.preventDefault();
        submitForm($(this));
    });

    // Handle total mass loss form submission
    $('#totalMassLossForm').on('submit', function (e) {
        e.preventDefault();
        submitTotalMassLossForm($(this));
    });

    // Toggle between API and manual inputs for total mass loss
    $('#useApiForTotalMassLoss').on('change', function() {
        if ($(this).is(':checked')) {
            $('#apiInputsTotalMassLoss').show();
            $('#manualInputsTotalMassLoss').hide();
            $('#totalMassLossForm input[name="use_api"]').val('true');
        } else {
            $('#apiInputsTotalMassLoss').hide();
            $('#manualInputsTotalMassLoss').show();
            $('#totalMassLossForm input[name="use_api"]').val('false');
        }
    });

    // Handle fetch exoplanet data button click
    $('#fetchExoplanetDataBtn').on('click', function() {
        const starName = $('#total_star_name').val();
        const planetName = $('#total_planet_name').val();

        if (!starName || !planetName) {
            alert('Por favor, insira o nome da estrela e do planeta.');
            return;
        }

        // Show loading indicator
        const btn = $(this);
        const originalBtnText = btn.text();
        btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Buscando...');

        // Fetch exoplanet data
        $.ajax({
            url: `/api/exoplanet/${starName}/${planetName}`,
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // Fill form fields with data
                    const data = response.data;
                    $('#total_stellar_radius').val(data.Restrela);
                    $('#total_stellar_mass').val(data.Mestrela);
                    $('#total_stellar_age').val(data.t_gyr);
                    $('#total_planet_radius').val(data.RplanetaEarth);
                    $('#total_planet_mass').val(data.MplanetaEarth);
                    $('#total_semi_major_axis').val(data.EixoMaiorPlaneta);
                    $('#total_eccentricity').val(data.Excentricidade);

                    // Set max_age to stellar age
                    $('#max_age').val(data.t_gyr);

                    // Turn off the API switch after fetching data
                    $('#useApiForTotalMassLoss').prop('checked', false).trigger('change');

                    alert('Dados carregados com sucesso!');
                } else {
                    alert('Erro ao buscar dados: ' + response.error);
                }
            },
            error: function() {
                alert('Erro ao conectar ao servidor. Por favor, tente novamente.');
            },
            complete: function() {
                // Reset button
                btn.prop('disabled', false).text(originalBtnText);
            }
        });
    });

    // Handle export velocity chart button click
    $('#exportVelocityBtn').on('click', function () {
        exportChart('velocity');
    });

    // Handle export density chart button click
    $('#exportDensityBtn').on('click', function () {
        exportChart('density');
    });

    // Handle export mass loss rates chart button click
    $('#exportMassLossRatesBtn').on('click', function () {
        exportMassLossRatesChart();
    });

    // Handle copy LaTeX table button click
    $('#copyLatexTableBtn').on('click', function () {
        copyTableAsLatex();
    });

    // Function to submit form data
    function submitForm(form) {
        // Hide any previous results or errors
        $('#resultsCard').hide();
        $('#errorAlert').hide();
        $('#totalMassLossResultsCard').hide();

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
            success: function (response) {
                if (response.success) {
                    // Display results
                    displayResults(response.results);
                } else {
                    // Display error
                    $('#errorMessage').text(response.error);
                    $('#errorAlert').show();
                }
            },
            error: function (xhr, status, error) {
                // Display error
                $('#errorMessage').text('Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente.');
                $('#errorAlert').show();
            },
            complete: function () {
                // Reset button
                submitBtn.prop('disabled', false).text(originalBtnText);
            }
        });
    }

    // Function to submit total mass loss form data
    function submitTotalMassLossForm(form) {
        // Hide any previous results or errors
        $('#resultsCard').hide();
        $('#totalMassLossResultsCard').hide();
        $('#errorAlert').hide();

        // Show loading indicator
        const submitBtn = form.find('button[type="submit"]');
        const originalBtnText = submitBtn.text();
        submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Calculando...');

        // Submit form data via AJAX
        $.ajax({
            url: '/calculate_total_mass_loss',
            type: 'POST',
            data: form.serialize(),
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    // Display total mass loss results
                    displayTotalMassLossResults(response.results);
                } else {
                    // Display error
                    $('#errorMessage').text(response.error);
                    $('#errorAlert').show();
                }
            },
            error: function (xhr, status, error) {
                // Display error
                $('#errorMessage').text('Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente.');
                $('#errorAlert').show();
            },
            complete: function () {
                // Reset button
                submitBtn.prop('disabled', false).text(originalBtnText);
            }
        });
    }

    // Function to display total mass loss results
    function displayTotalMassLossResults(results) {
        // Store results globally for use in export
        calculationResults = results;

        // Populate star and planet properties
        $('#total_result_idade_estrela').text(results.idade_estrela);
        $('#total_result_r_estelar_rsol').text(results.r_estelar_rsol);
        $('#total_result_massa_estrela_msol').text(results.massa_estrela_msol);
        $('#total_result_r_planeta_rterra').text(results.r_planeta_rterra);
        $('#total_result_m_planeta_mterra').text(results.m_planeta_mterra);
        $('#total_result_semi_eixo').text(results.semi_eixo);
        $('#total_result_planeta_excentricidade').text(results.planeta_excentricidade);

        // Populate simulation parameters
        $('#total_result_fator_de_eficiencia').text(results.fator_de_eficiencia);
        $('#total_result_min_age').text(results.min_age + ' Gyr');
        $('#total_result_max_age').text(results.max_age + ' Gyr');

        // Populate mass loss results
        $('#total_result_mass_loss_photoev').text(results.mass_loss_photoev);
        $('#total_result_mass_loss_wind').text(results.mass_loss_wind);
        $('#total_result_total_mass_loss').text(results.total_mass_loss);
        $('#total_result_total_mass_loss_percent').text(results.total_mass_loss_percent);

        // Populate detailed results table
        const tableBody = $('#detailedResultsTableBody');
        tableBody.empty();

        const ages = results.results_data.ages;
        const fx_values = results.results_data.fx_values;
        const temperatures = results.results_data.temperatures;
        const wind_velocities = results.results_data.wind_velocities;
        const wind_densities = results.results_data.wind_densities;
        const photoevap_rates = results.results_data.photoevap_mass_loss_rates;
        const wind_rates = results.results_data.wind_mass_loss_rates;
        const total_rates = results.results_data.total_mass_loss_rates;

        for (let i = 0; i < ages.length; i++) {
            const row = $('<tr>');
            row.append($('<td>').text(ages[i].toFixed(2)));
            row.append($('<td>').text(fx_values[i].toExponential(2)));
            row.append($('<td>').text((temperatures[i] / 1e6).toFixed(2)));
            row.append($('<td>').text((wind_velocities[i] / 1e5).toFixed(2)));
            row.append($('<td>').text(wind_densities[i].toExponential(2)));
            row.append($('<td>').text(photoevap_rates[i].toExponential(2)));
            row.append($('<td>').text(wind_rates[i].toExponential(2)));
            row.append($('<td>').text(total_rates[i].toExponential(2)));
            tableBody.append(row);
        }

        // Create mass loss rates chart
        createMassLossRatesChart(ages, wind_rates, photoevap_rates, total_rates);

        // Show results card
        $('#totalMassLossResultsCard').show();

        // Scroll to results
        $('html, body').animate({
            scrollTop: $('#totalMassLossResultsCard').offset().top - 20
        }, 500);
    }

    // Function to create mass loss rates chart
    function createMassLossRatesChart(ages, wind_rates, photoevap_rates, total_rates) {
        const ctx = document.getElementById('massLossRatesChart').getContext('2d');

        // Destroy existing chart if it exists and has a destroy method
        if (window.massLossRatesChart && typeof window.massLossRatesChart.destroy === 'function') {
            window.massLossRatesChart.destroy();
        }

        // Create new chart
        window.massLossRatesChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ages,
                datasets: [
                    {
                        label: 'Vento Estelar',
                        data: wind_rates,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderWidth: 2,
                        pointRadius: 3,
                        fill: false
                    },
                    {
                        label: 'Fotoevaporação',
                        data: photoevap_rates,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderWidth: 2,
                        pointRadius: 3,
                        fill: false
                    },
                    {
                        label: 'Total',
                        data: total_rates,
                        borderColor: 'rgba(153, 102, 255, 1)',
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        borderWidth: 2,
                        pointRadius: 3,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Idade (Gyr)'
                        }
                    },
                    y: {
                        type: 'logarithmic',
                        title: {
                            display: true,
                            text: 'Taxa de Perda de Massa (g/s)'
                        },
                        ticks: {
                            callback: function(value, index, values) {
                                return value.toExponential(0);
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y.toExponential(2) + ' g/s';
                            }
                        }
                    }
                }
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
        $('#result_fx').text(results.fx);
        $('#result_r_estelar_rsol').text(results.r_estelar_rsol);
        $('#result_massa_estrela_msol').text(results.massa_estrela_msol);
        $('#result_r_planeta_rterra').text(results.r_planeta_rterra);
        $('#result_m_planeta_mterra').text(results.m_planeta_mterra);
        $('#result_semi_eixo').text(results.semi_eixo);
        $('#result_planeta_excentricidade').text(results.planeta_excentricidade);
        $('#result_txmass_loss_photoev').text(results.tx_mass_loss_photoev);
        $('#result_mass_loss_photoev').text(results.mass_loss_photoev);
        $('#result_mass_loss_photoev_percent').text(results.mass_loss_photoev_percent);
        $('#result_txmass_loss_wind').text(results.tx_mass_loss_wind);
        $('#result_mass_loss_wind').text(results.mass_loss_wind);
        $('#result_mass_loss_wind_percent').text(results.mass_loss_wind_percent);
        $('#result_total_mass_loss').text(results.total_mass_loss);
        $('#result_total_mass_loss_percent').text(results.total_mass_loss_percent);
        $('#result_velocidade_vento_estelar').text(results.velicidade_vento_estelar);
        $('#result_densidade_vento_estelar').text(results.densidade_vento_estelar);
        $('#result_fator_de_eficiencia').text(results.fator_de_eficiencia);
        $('#result_velocidade_inicial').text(results.velocidade_inicial);
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
                            callback: function (value, index, values) {
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
                            filter: function (value, index, values) {
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
                            callback: function (value, index, values) {
                                return formatPowerOfTen(value);
                            },
                            major: {
                                enabled: true
                            },
                            minor: {
                                enabled: false,
                                display: false
                            },
                            filter: function (value, index, values) {
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
                            title: function (context) {
                                return `Distância: ${context[0].parsed.x.toExponential(2)} Rsol`;
                            },
                            label: function (context) {
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
                            callback: function (value, index, values) {
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
                            title: function (context) {
                                return `Distância: ${context[0].parsed.x.toExponential(2)} au`;
                            },
                            label: function (context) {
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

    // Function to export mass loss rates chart as PNG
    function exportMassLossRatesChart() {
        if (!window.massLossRatesChart) {
            alert('Nenhum dado de gráfico disponível para exportar.');
            return;
        }

        const chart = window.massLossRatesChart;
        const title = 'Taxas de Perda de Massa vs Idade';
        const xLabel = 'Idade (Gyr)';
        const yLabel = 'Taxa de Perda de Massa (g/s)';

        // Extract data from the chart
        const xData = chart.data.labels;
        const windRates = chart.data.datasets[0].data;
        const photoevapRates = chart.data.datasets[1].data;
        const totalRates = chart.data.datasets[2].data;

        // Show loading indicator on the button
        const $btn = $('#exportMassLossRatesBtn');
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
                chart_type: 'mass_loss_rates',
                x_data: xData,
                y_data: totalRates, // Use total rates as primary data
                x_label: xLabel,
                y_label: yLabel,
                title: title,
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
            a.download = 'mass_loss_rates_chart.png';
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

    // Function to convert HTML table to LaTeX format and copy to clipboard
    function copyTableAsLatex() {
        // Get the table
        const table = document.getElementById('detailedResultsTable');
        if (!table) {
            alert('Tabela não encontrada.');
            return;
        }

        // Start building LaTeX table
        let latexCode = '\\begin{table}[htbp]\n';
        latexCode += '\\centering\n';
        latexCode += '\\caption{Resultados Detalhados por Idade}\n';
        latexCode += '\\begin{tabular}{';

        // Add column specifications based on the number of columns
        const headerRow = table.querySelector('thead tr');
        if (!headerRow) {
            alert('Cabeçalho da tabela não encontrado.');
            return;
        }

        const numColumns = headerRow.cells.length;
        for (let i = 0; i < numColumns; i++) {
            latexCode += 'c';
        }
        latexCode += '}\n\\hline\n';

        // Add header row
        const headers = [];
        for (let i = 0; i < headerRow.cells.length; i++) {
            headers.push(headerRow.cells[i].textContent.trim());
        }
        latexCode += headers.join(' & ') + ' \\\\ \\hline\n';

        // Add data rows
        const tbody = table.querySelector('tbody');
        if (!tbody) {
            alert('Corpo da tabela não encontrado.');
            return;
        }

        const rows = tbody.querySelectorAll('tr');
        for (let i = 0; i < rows.length; i++) {
            const cells = rows[i].querySelectorAll('td');
            const rowData = [];

            for (let j = 0; j < cells.length; j++) {
                rowData.push(cells[j].textContent.trim());
            }

            latexCode += rowData.join(' & ') + ' \\\\ \n';
        }

        // Close the LaTeX table
        latexCode += '\\hline\n\\end{tabular}\n';
        latexCode += '\\label{tab:detailed_results}\n';
        latexCode += '\\end{table}';

        // Copy to clipboard
        try {
            navigator.clipboard.writeText(latexCode).then(
                function() {
                    // Show success message
                    alert('Tabela copiada para a área de transferência em formato LaTeX.');
                }, 
                function() {
                    // Fallback for older browsers
                    const textarea = document.createElement('textarea');
                    textarea.value = latexCode;
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    alert('Tabela copiada para a área de transferência em formato LaTeX.');
                }
            );
        } catch (err) {
            // Fallback for browsers that don't support clipboard API
            const textarea = document.createElement('textarea');
            textarea.value = latexCode;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            alert('Tabela copiada para a área de transferência em formato LaTeX.');
        }
    }
});
