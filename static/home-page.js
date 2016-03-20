window.onload = function () {
    $("#conversation-code")
        .keypress( function(evt) {
            console.log(evt.which)
            if (evt.which == 13) {
                $("#conversation-button").click();
            }
        
            linkButton = $("#conversation-button");
            href = linkButton.attr("href");
            linkButton.attr("href", href.concat(String.fromCharCode(evt.charCode)));
        });
    };
