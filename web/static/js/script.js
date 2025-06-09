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

        // Show results card
        $('#resultsCard').show();

        // Scroll to results
        $('html, body').animate({
            scrollTop: $('#resultsCard').offset().top - 20
        }, 500);
    }
});
