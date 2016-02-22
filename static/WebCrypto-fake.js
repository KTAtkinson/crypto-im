window.crypto.subtle.generateKey = function(algo, extractable, key_ops) {
    return {
        key_string: 'testkeydontuse',
        encrypt: function(alg, key, data) {
            return this.key_string.concat('*//*', msg)
            },
        decrypt: function(alg, key, data) {
            return msg.split('*//*')[1];
            },
        public_key: {},
        private_key: {},
    }
}
