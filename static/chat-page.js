function sendMessage(evt) {
    evt.preventDefault();
    var messageInput = evt.target.querySelector('textarea[name="message"]');
    var messageText = $(messageInput).val();
    console.log(user_id, messageText);
    
     var messages_dict_list = [];
     for (var i=0; i<conversation_users.length; i++) {
        console.log("USER: " + conversation_users[i]);
        messages_dict_list.push({
                'user_id': conversation_users[i].user_id,
                'encoded_message': messageText
       });
    }
    messages_dict_list.push({
            'user_id': user_id,
            'encoded_message': messageText
    });
    console.log(messages_dict_list);

    var request = JSON.stringify({'encoded_messages': messages_dict_list});
    // var request = {'key': [{'user_id': user_id}, {'key1', messageText}]};
    console.log(request);
    
    $.ajax('/add_message/' + c_id + '/' + user_id,
           {'method':'POST', 'data':request})
           .always(function() {
                var error_container = $('#conversation-pane .error');
                error_container
                    .hide()
                    .text('');
                console.log('Cleared past errors.')
            })
           .done(function(data, status_text, xhr) {
                   $(messageInput).val('');
                   console.log('Message added.')
               })
           .fail(function(xhr, status_text, err) {
                console.log('MESSAGE COuLD NOT BE ADDED', err);
                var error_container = $('#conversation-pane .error');
                error_container.text(rsp.error || err);
                error_container.show();
                })
}
 

function pollForMessages(conversation_id, user_id, interval) {
    var last_message_id = $('#conversation .chat-message:last').data('mid') || null;
    request = {
            'public_key': '',
            'last_message_seen_id': last_message_id
            }
    console.log('LAST MESSAGE SEEN ID:' + last_message_id)

    $.ajax('/status/' + conversation_id + '/' + user_id,
           {'method': 'POST', 'data':request})
           .always(function() {
                var error_container = $('#conversation-pane .error');
                error_container.hide(); error_container.text(''); }) .error(function(rsp, status_text, err) {
                var error_container = $('#conversation_-pane .error');
                error_container.text(rsp.data.error || "There was a server error.")
                error_container.show();
                window.setTimeout(pollForMessages, interval*1.5, conversation_id, user_id, TIMEOUT*1.5);
                })
           .done(function(resp) {
                var newMessages = resp.new_messages;
                var chatStream = document.getElementById('conversation');
                for (var i = 0; i < newMessages.length; i++) {
                    var rawMessage = newMessages[i];
                    console.log(rawMessage);
                    var newEntry = document.createElement('div');
                    $(newEntry)
                        .addClass('chat-message')
                        .addClass('container')
                        .attr('data-mid', rawMessage.message_id)
                    var userImage = document.createElement('span');
                    $(userImage)
                        .addClass("user-image")
                        .addClass("glyphicon glyphicon-user")
                        .addClass('col-md-1');
                    newEntry.appendChild(userImage)

                    var msgContent = document.createElement("div");
                    $(msgContent)
                        .addClass("message-content")
                        .addClass("col-md-11");
                    newEntry.appendChild(msgContent);

                    var authorName = document.createElement("div");
                    $(authorName)
                        .addClass("author")
                        .text(rawMessage.sender_name);
                    msgContent.appendChild(authorName);

                    var msgText = document.createElement("div");
                    $(msgText)
                        .addClass("message")
                        .text(rawMessage.message);
                    msgContent.appendChild(msgText);

                    chatStream.appendChild(newEntry);
                    window.scrollTo(0, document.body.scrollHeight);
                }

                window.conversation_users = resp.users
                window.setTimeout(pollForMessages, interval, conversation_id, user_id, TIMEOUT);
           });
}

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
    $('#send-message-form').submit(sendMessage);
    pollForMessages(c_id, user_id, TIMEOUT);
}


function joinChat(evt) {
    evt.preventDefault();
    window.form = evt.currentTarget;
    var public_key = $(form.querySelector('textarea[name="pkey"]')).val();
    window.private_key = $(form.querySelector('textarea[name="private-key"]')).val();


    var request = {
        name: $('form input[name="name"').val(),
        // Adding public key as empty string for now.
        public_key: public_key
        };
    console.log(request);
    $.ajax({
        'url': '/join/' + c_code,
        'data': request,
        'method': 'POST'
        })
        .always(beforeFormSubmit)
        .success(joinSuccess)
        .error(addError);
}


var c_code = $('#conversation-pane').data('ccode');
$('#add-user-form').submit(joinChat);
var TIMEOUT = 100;
