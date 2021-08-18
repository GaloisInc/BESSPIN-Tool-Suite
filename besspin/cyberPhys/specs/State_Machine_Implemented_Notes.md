# State Machine Implementation Notes

**bold** face means that the step was referenced inside of 
the state machine diagram. Regular face means that the step 
was not referenced inside the state machien diagram. 

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
* Where are the activity monitors (noncrit)?
* What does load device drivers mean?

## Non-Critical Component Failure State
### State Entry Procedure
* **Log error**
### Questions
* out of date--more than just LED failure?

## Terminate State
### State Entry Procedure
* **exit from component handler**
### Questions
* what does orderly shutdown mean?

## Ready State
### State Entry Procedure
* setup for transition even determination
    * start the timeout timer
    * wait for cc msg

### Questions
* what does up mean--do we monitor this?

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
* what is demo mode and how does it evolve in time?

## CAN State
this is kind of ignored for now. The can state machine runs in paralle
with ignition.

## CC State
* restart
* hack active
* active scenario
* driving mode
