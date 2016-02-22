function strToArrayBufferView(str) {
    return Uint8Array(str
            .split('')
            .map( function(e) { return e.charCodeAt(0)}));
}

function arrayBufferViewToStr(bufferView) {
    return Array.from(bufferView)
                   .map( function(e) { return String.fromCharCode(e); } )
                   .join('');
}

