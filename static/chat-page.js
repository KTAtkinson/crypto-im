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


function joinSuccess(data) {
    window.user_id = data.new_user_id;
    window.c_id = data.conversation_id;
    console.log(c_id);
    $("#add-user-form").hide();
    $("#conversation-pane").show();
}


unction joinChat(evt) {
    evt.preventDefault();

    var request = {
        name: $('form input[name="name"').val(),
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
        .success(joinSuccess)
        .fail(addError);
}


var c_code = $('#conversation-pane').data('ccode');
$('form').submit(joinChat);
