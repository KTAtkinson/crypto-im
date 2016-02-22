window.crypto.subtle.generateKey = function(args) {
    return {
        key: args['key_string'],
        encrypt: function(msg) {
            return this.key.concat('*//*', msg)
            },
        decrypt: function(msg) {
            return msg.split('*//*')[1];
            },
    }
}
