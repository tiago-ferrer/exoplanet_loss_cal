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
        // Populate result fields
        $('#result_lx').text(results.lx);
        $('#result_t_cor').text(results.t_cor);
        $('#result_mass_loss_photoev').text(results.mass_loss_photoev);
        $('#result_mass_loss_photoev_percent').text(results.mass_loss_photoev_percent);
        $('#result_mass_loss_wind').text(results.mass_loss_wind);
        $('#result_mass_loss_wind_percent').text(results.mass_loss_wind_percent);
        $('#result_total_mass_loss').text(results.total_mass_loss);
        $('#result_total_mass_loss_percent').text(results.total_mass_loss_percent);

        // Create the density vs distance chart
        if (results.density_vs_distance) {
            createDensityDistanceChart(results.density_vs_distance);
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
    function createDensityDistanceChart(data) {
        const ctx = document.getElementById('densityDistanceChart').getContext('2d');

        // Configuration for major tick intervals (change these values to control the interval)
        const xAxisTickStep = 10; // Interval between major ticks on x-axis (in powers of 10)
        const yAxisTickStep = 10; // Interval between major ticks on y-axis (in powers of 10)

        // Destroy existing chart if it exists
        if (window.densityChart) {
            window.densityChart.destroy();
        }

        // Create new chart
        window.densityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.distances,
                datasets: [{
                    label: 'Densidade do Vento Estelar (cm⁻³)',
                    data: data.densities,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
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
                            text: 'Distância (Rsol em cm)'
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
                            text: 'Distância (km)'
                        },
                        ticks: {
                            beginAtZero: true,
                            callback: function(value, index, values) {
                                return formatPowerOfTenLinear(value);
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
                            text: 'Velocidade do Vento Estelar(m/s)'
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
                                return `Distância: ${context[0].parsed.x.toExponential(2)} km`;
                            },
                            label: function(context) {
                                return `Velocidade: ${context.parsed.y.toExponential(2)} m/s`;
                            }
                        }
                    }
                }
            }
        });
    }
});
