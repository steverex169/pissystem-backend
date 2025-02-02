(function($) {
    $(function() {
        $('.module > h2').css('display', 'none');

        var selectField = $('#id_method'),
            verified = $('.field-equipment_id');

        function toggleVerified(value) {
            if (value === 'Equipment') {
                verified.show();
            } else {
                verified.hide();
            }
        }

        // show/hide on load based on existing value of selectField
        toggleVerified(selectField.val());

        // show/hide on change
        selectField.change(function() {
            toggleVerified($(this).val());
        });
    });

    $(function() {
        $('.module > h2').css('display', 'none');

        var selectField = $('#id_is_corporate_user'),
            verified = $('.field-corporate_unique_id');

        function toggleVerified(value) {
            if (value === 'Yes') {
                verified.show();
            } else {
                verified.hide();
            }
        }

        // show/hide on load based on existing value of selectField
        toggleVerified(selectField.val());

        // show/hide on change
        selectField.change(function() {
            toggleVerified($(this).val());
        });
    });
})(django.jQuery);