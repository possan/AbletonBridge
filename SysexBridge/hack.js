
var midi = require('midi');

var INPUT_NAME = 'IAC Driver CUBEPLUG_OUT';
var OUTPUT_NAME = 'IAC Driver CUBEPLUG_IN';

var input = new midi.input();
var output = new midi.output();

for(var j=0; j<input.getPortCount(); j++) {
  console.log('Input #' + j +': ' + input.getPortName(j));
  if (input.getPortName(j) == INPUT_NAME) {
    console.log('Opening input port #' + j);
    input.openPort(j);
  }
}

for(var j=0; j<output.getPortCount(); j++) {
  console.log('Output #' + j +': ' + output.getPortName(j));
  if (output.getPortName(j) == OUTPUT_NAME) {
    console.log('Opening output port #' + j);
    output.openPort(j);
  }
}

console.log();

// https://www.cs.cf.ac.uk/Dave/Multimedia/node158.html
// Configure a callback.
input.ignoreTypes(false, false, false);

function SysexResponseToJson(message) {
  console.log('Got MIDI Message: ' + JSON.stringify(message));
  var bytes = message.slice(2, message.length - 1);
  console.log('bytes', bytes);
  var json = bytes.map(function(i) { return String.fromCharCode(i); }).join('');
  return JSON.parse(json);
}

function JsonToSysexRequest(json) {
  if (typeof(json) == 'object') json = JSON.stringify(json);
  console.log('Sending JSON String: ' + json);
  var bytes = json.split('').map(function(c) { return c.charCodeAt(0) } );
  bytes = [0xF0, 0x6A].concat(bytes, [0xF7]);
  // console.log('Sending MIDI Bytes: ' + JSON.stringify(bytes));
  return bytes;
}




input.on('message', function(deltaTime, message) {
  // console.log('Incoming message m:' + message + ' d:' + deltaTime);
  if (message[0] == 0xF7 && message[1] == 0x4A) {
    var response = SysexResponseToJson(message);
    console.log('Incoming response: ' + JSON.stringify(response, null, 2));
  } else {
    console.log('Incoming response: ' + JSON.stringify(message));
  }
});

// output.sendMessage([176,22,1]);

var k = 0;
setInterval(function() {
  console.log('Sending sysex ping');
  switch(k) {
    case 0:
      output.sendMessage(JsonToSysexRequest({ Q:'time' }));
      break;
    case 1:
      output.sendMessage(JsonToSysexRequest({ Q:'tracks' }));
      break;
    case 2:
      output.sendMessage(JsonToSysexRequest({ A:'track-props', TR: 2, s1: Math.random(), s2: Math.random(), vol: Math.random() }));
      break;
    case 3:
      output.sendMessage(JsonToSysexRequest({ Q:'clip-notes', TR: 0, SL: 0 }));
      break;
    case 4:
      notes = []
      for(var j=0; j<16; j++) {
        notes.push({
          S: j,
          N: Math.floor(12 + Math.random() * 24),
          D: 0.5 + Math.random() * 0.5,
          V: 127
        });
      }
      output.sendMessage(JsonToSysexRequest({ A:'set-notes', TR: 0, SL: 0, notes: notes }));
      break;
    case 5:
      notes = []
      for(var j=0; j<16; j++) {
        notes.push({
          S: j,
          N: Math.floor(12 + Math.random() * 24),
          D: 0.5 + Math.random() * 0.5,
          V: 127
        });
      }
      output.sendMessage(JsonToSysexRequest({ A:'set-notes', TR: 0, SL: 2, notes: notes }));
      break;
  }
  k ++;
  k %= 6;
  // output.sendMessage([0xF0, 0, 10,11,12,13,14,15, 42, 41, 40, 10, 0xF7]);
}, 50);

