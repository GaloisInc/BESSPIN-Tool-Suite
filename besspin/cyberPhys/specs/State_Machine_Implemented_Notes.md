# State Machine Implementation Notes

**bold** face means that the step was referenced inside of 
the state machine diagram. Regular face means that the step 
was not referenced inside the state machien diagram. 

* mixup of levels of abstraction
* mapping from components to an actual state machine
	* assume other components are "correct"
	* director is the most stateful
	* focusing on the director for now


## Startup Notes
### State Entry Procedure
* Kill existing processes
* **Startup the simulator**
* Start the can bus multiverse
* Start location poller
* Start infotainment UI handler
* Start infotainment audio player
* Start the infotainment can bus
* **Start the LED manager (noncrit)**
* Start the speedomete (noncrit)
### Questions
* Where are the activity monitors (noncrit)? <- this in the code now. push all health monitoring into a separate component. CAPTURE IN THE SPECS
* What does load device drivers mean? <- remove this from spec

## Non-Critical Component Failure State
### State Entry Procedure
* **Log error**
### Questions
* out of date--more than just LED failure? <- can be removed. Track failure of these components.

## Terminate State
### State Entry Procedure
* **exit from component handler**
### Questions
* what does orderly shutdown mean? <- has evolved. ignition should never exit?

## Ready State
### State Entry Procedure
* setup for transition even determination
    * start the timeout timer
    * wait for cc msg
### Questions
* what does up mean--do we monitor this? <- no need for health monitor here

## Self Drive State
### State Entry Procedure
* send self drive command to simulator service
### Questions

## Timeout State
### State Entry Procedure
* nothing -- go to restart
### Questions
* why is this here?


## Restart State
### State Entry Procedure
* send restart command to the simulator
### Questions
* what is demo mode and how does it evolve in time? <- demo mode is self drive mode

## CAN State
this is kind of ignored for now. The can state machine runs in parallel
with ignition.

## CC State
* restart
* hack active
* active scenario
* driving mode


# Infotainment Notes
* ui looks at info net
* player looks at the can multiverse

* poller goes direct to server
* ui sends the button press to multiverse and internal network
* server sends state to the player
* player also forwards the position to the ui again (why??)


# Next Steps
* Waiting for components to come up online (no need)
* Minimal level of functionality
* Health: working on a diagnostics tool--work for the heartbeat monitor
