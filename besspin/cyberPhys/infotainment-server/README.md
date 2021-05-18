===Infotainment Server===

The Infotainment Server (IS) is the component of the Infotainment system that runs on the P2 and communicates with the Infotainment UI and the Simulator. All communication is done via CAN packets. CAN packets _from_ the UI are received by the IS directly; CAN packets _to_ the UI are routed through the Security Mux. CAN packets _from_ the Simulator (or from the Python script controlling the Simulator), consisting of the vehicle's position, are received by the IS directly; the IS does not generate CAN packets _to_ the Simulator.

==Description/Functionality==

The IS is a simple event loop-based server. Every time through the loop, it listens on the CAN bus for a control packet from the UI or the simulator, modifies its local state  accordingly, and sends a reply packet to the Security Mux.

The overall state machine for the IS is, therefore, relatively simple; it consists of 3 independent state machines: one for the volume control, one for the music selection, and one for the position information. 

