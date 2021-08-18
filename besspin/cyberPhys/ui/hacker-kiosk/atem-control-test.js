const { Atem } = require('atem-connection')
const myAtem = new Atem()
myAtem.on('info', console.log)
myAtem.on('error', console.error)

myAtem.connect('192.168.10.240')

myAtem.on('connected', () => {
	myAtem.changeProgramInput(2).then(() => {
		// Fired once the atem has acknowledged the command
		// Note: the state likely hasnt updated yet, but will follow shortly
		console.log('Program input set')
	})
	console.log(myAtem.state)
})

myAtem.on('stateChanged', (state, pathToChange) => {
	console.log(state) // catch the ATEM state.
})
