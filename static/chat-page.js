function beforeFormSubmit() {
    var errorContainer = $(form).find('error');
    errorContainer.hide();
    errorContainer.text('');
}


function addError(resp) {
    var messageContainer = $(form).find('.error');
    messageContainer.text(resp.responseJSON.error);
    messageContainer.show();
}


function joinChat(evt) {
    evt.preventDefault();
    window.form = evt.target;

    var request = {
        name: $('form input[name="name"]').val(),
        // Adding public key as empty string for now.
        public_key: ''
        };
    console.log(request);
    $.ajax({
        'url': '/join/' + c_code,
        'data': request,
        'method': 'POST'
        })
        .always(beforeFormSubmit)
        .success(function(data) {
            window.user_id = data.new_user_id;
            })
        .fail(addError);
}


var c_code = $('#conversation').data('ccode');
$('form').submit(joinChat);
