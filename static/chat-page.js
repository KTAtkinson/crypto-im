function getCookieInfo() {
    var cookies = document.cookie.split(";");

    var uId, cId
    for (var i=0; i<cookies.length; i++) {
        var cookie = cookies[i].split("=");
        if (cookie[0].trim() == cookieKey) {
            var values = cookie[1].split(":");
            var uId = values[0];
            var cId = values[1];
            break;
        }
    }
    return [uId, cId]
}


function sendMessage(evt) {
    var cookieData = getCookieInfo();
    var uId = cookieData[0];
    var cId = cookieData[1];
    evt.preventDefault();
    
    var messageInput = evt.target.querySelector('textarea[name="message"]');
    var messageText = $(messageInput).val();
    
    var encodePromises = []
    var recipientData = conversation_users.concat([{user_id: uId, public_key: JSON.stringify(publicJWK)}]);

    for (var i=0; i<recipientData.length; i++) {
        var recipient = recipientData[i];
        encodePromises.push(encryptMessage(recipient.user_id, recipient.public_key, messageText));
    }

    Promise.all(encodePromises)
        .then(
            function(msgs) {
                var msgsObj = {}
                for (var i=0; i<msgs.length; i++) {
                    msgsObj[i] = msgs[i];
                }
                var request = {'encoded_messages': JSON.stringify(msgsObj)};
                // var request = {'key': [{'user_id': user_id}, {'key1', messageText}]};
        
                $.ajax('/add_message/' + cId + '/' + uId,
                       {'method':'POST', 'data':request})
                    .always(function() {
                            var error_container = $('#conversation-pane .error');
                            error_container
                                .hide()
                                .text('');
                        })
                       .done(function(data, status_text, xhr) {
                               $(messageInput).val('');
                           })
                       .fail(function(xhr, status_text, err) {
                            var error_container = $('#conversation-pane .error');
                            error_container.text(err);
                            error_container.show();
                            })},
            function(err) {console.log(err)});
}


function encryptMessage(recieverId, rPublicKey, msgText) {
    return new Promise (
        function(resolve, reject) {
            crypto.subtle.importKey("jwk", JSON.parse(rPublicKey),
                                    {name: "RSA-OAEP", modulusLength: 2048,
                                    publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
                                    hash: {name: "SHA-256"}}, true, ["encrypt"])
                .then(
                    function(key) {
                        var msgBuffer = strToArrayBufferView(msgText);
                        crypto.subtle.encrypt({name: "RSA-OAEP", iv: vector}, key,
                                              msgBuffer)
                            .then(
                                function(strBuffer) { 
                                    var encodedStr = new Uint8Array(strBuffer);
                                    encodedStr = encodedStr.toString();
                                    resolve({ 'user_id': recieverId,
                                              'encoded_message': encodedStr})},
                                function(err) {
                                    reject("Failed to encrypt message: " + err);
                                });
                   },
                   function(err) {reject("Failed to load private key: " + err)});
     });
}


function addMessages(stream, msgs) {
    if (msgs.length === 0) {
        return;
    }
    
    var workingMsg = msgs[0];
    var msgBuffer = new Uint8Array(workingMsg.message.split(","));
    crypto.subtle.decrypt({name: "RSA-OAEP", iv: vector}, privateKey, msgBuffer)
        .then(function(textBuffer) {
                    var msgText = arrayBufferViewToStr(new Uint8Array(textBuffer));

                    var newEntry = document.createElement('div');
                    $(newEntry)
                        .addClass('chat-message')   
                        .addClass('container')
                        .attr('data-mid', workingMsg.message_id)
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
                        .text(workingMsg.sender_name);
                    msgContent.appendChild(authorName);

                    var msgTextDiv = document.createElement("div");
                    $(msgTextDiv)
                        .addClass("message")
                        .text(msgText);
                    msgContent.appendChild(msgTextDiv);

                    stream.appendChild(newEntry);
                    window.scrollTo(0, document.body.scrollHeight);
                    addMessages(msgs.slice(1));},
              function(err) {console.log(err)
                    });
}


function pollForMessages(conversation_id, user_id, interval) {
    var cookieData = getCookieInfo();
    var uId = cookieData[0];
    var cId = cookieData[1];
    console.log("USER ID: " + uId + "CONVERSATION ID: " + cId)
    var last_message_id = $('#conversation .chat-message:last').data('mid') || null;
    request = {
            'public_key': JSON.stringify(publicJWK),
            'last_message_seen_id': last_message_id
            }

    $.ajax('/status/' + cId + '/' + uId,
           {'method': 'POST', 'data':request})
           .always(function() {
                var error_container = $('#conversation-pane .error');
                error_container.hide();
                error_container.text(''); }) 
           .error(function(rsp, status_text, err) {
                var error_container = $('#conversation_-pane .error');
                error_container.text(rsp.data.error || "There was a server error.")
                error_container.show();
                window.setTimeout(pollForMessages, interval*1.5, conversation_id, user_id, TIMEOUT*1.5);
                })
           .done(function(resp) {
                var newMessages = resp.new_messages;
                var chatStream = document.getElementById('conversation');
                addMessages(chatStream, newMessages);
                window.conversation_users = resp.users;
                window.setTimeout(pollForMessages, interval, cId, uId, TIMEOUT);
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
    crypto.subtle.generateKey({name: "RSA-OAEP", modulusLength: 2048,
                              publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
                              hash: {name: "SHA-256"}}, true, ["encrypt", "decrypt"])
        .then(function(newKey) {
                    publicKey = newKey.publicKey;
                    privateKey = newKey.privateKey;
                    crypto.subtle.exportKey("jwk", publicKey)
                        .then(function(jwk){
                                    window.publicJWK = jwk;},
                              function() {})},
              function() {});
    window.cookieKey = "chat-data-" + data.conversation_id.toString()
    $("#add-user-form").hide();
    $("#conversation-pane").show();
    $('#send-message-form').submit(sendMessage);
    pollForMessages(data.conversation_id, data.user_id, TIMEOUT);
}


function joinChat(evt) {
    evt.preventDefault();
    window.form = evt.currentTarget;
    var public_key = $(form.querySelector('textarea[name="pkey"]')).val();
    window.private_key = $(form.querySelector('textarea[name="private-key"]')).val();

    var request = {
        name: $('form input[name="name"').val(),
        // Adding public key as empty string for now.
        public_key: publicKey
        };
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
var TIMEOUT = 1000;
var publicKey = null;
var privateKey = null;
var publicJWK = null;
var vector = crypto.getRandomValues(new Uint8Array(16));
var cookieKey = null;
