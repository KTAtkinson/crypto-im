var bv = require('../static/bufferView.js');
describe('Test buffer view', function() {
    it('convert string into an array of char codes.', function() {
        var output = bv.strToArrayBufferView('this');
        expect(output).toEqual(new Uint8Array([116, 104, 105, 115]));
    });

    it("array buffer to a string", function() {
        var chars = bv.arrayBufferViewToStr(new Uint8Array([116, 104, 105, 115]));
        expect(chars).toEqual('this');
    });
});

