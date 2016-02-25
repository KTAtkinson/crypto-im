window.crypto.subtle.generateKey = function(algo, extractable, key_ops) {
    return new Promise(function(fulfill, reject) {
        this.keyValue = function() {
            var bufferView =  new Uint8Array(12);
            for (var chr=0; chr<12; chr++){
                bufferView[chr] = Math.floor(Math.random() * 94) + 35;
                }
            return bufferView;
           }();
        this.publicKey = this.keyValue;
        this.privateKey = this.keyValue;

        fulfill(this);
        });
}

window.crypto.subtle.exportKey = function(format, key_object) {return new Promise( function(fulfill, error) {
    var json_key = JSON.stringify({"key_value": key_object);
    console.log("KEY JSON: " + json_key);
    fulfill(JSON.stringify(key_json))}); };

window.crypto.subtle.importKey = function(format, keyData, algo, extractable, usages) {
    return new Promise(function(fulfill, error) {
        var newKey = window.crypto.subtle.generateKey()
            .then(function(newKey) {
                    keyData = JSON.parse(keyData);
                    newKey.keyValue = newKey.publicKey = newKey.privateKey = keyData;
                    fulfill(newKey)},
                function() {});
    });
}

window.crypto.subtle.encrypt = function(algo, key, data) {
    return new Promise( function(fulfill, error) {
            var encrypted_data = new Uint8Array(key.length+data.length);
            encrypted_data.set(key, 0);
            encrypted_data.set(data, key.length);
            fulfill(encrypted_data);
            });
}

window.crypto.subtle.decrypt = function(algo, key, data) {
    return new Promise( function(fulfill, error) {
            fulfill(data.slice(key.length));
    });
}
