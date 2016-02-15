function joinChat(evt) {
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
        .success(function(data) {
            window.user_id = data.new_user_id;
            });
}


var c_code = $('#conversation').data('ccode');
$('form').submit(joinChat);
