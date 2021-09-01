#!/usr/bin/env node
const { Atem } = require('atem-connection')
const myAtem = new Atem()
myAtem.on('info', console.log)
myAtem.on('error', console.error)


var args = process.argv.slice(2);
var channel = parseInt(args[0]);
console.log(channel);
if(channel !== 1 && channel !== 2) {
  console.log("invalid channel argument");
  return;
}


myAtem.connect('192.168.10.240')

myAtem.on('connected', () => {
	myAtem.changeProgramInput(channel).then(() => {
		// Fired once the atem has acknowledged the command
		// Note: the state likely hasnt updated yet, but will follow shortly
		console.log('Program input set')
	})
	console.log(myAtem.state)
})

myAtem.on('stateChanged', (state, pathToChange) => {
	console.log(state) // catch the ATEM state.
})
