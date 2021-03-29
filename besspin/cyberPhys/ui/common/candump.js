
// Project: SSITH CyberPhysical Demonstrator
// Name: candump.js
// Author: Steven Osborn <steven@lolsborn.com>
// Date: 1 December 2020

// Dumps all CAN traffic on CyberPhys network to stdout

import {CanNetwork, CanListener} from './can.js';

const CAN_NETWORK_PORT = 5002;

let can = new CanNetwork(CAN_NETWORK_PORT);
can.register(new CanListener(function(msg) {
  let id = msg.id.toString(16).toUpperCase();
  console.log(`id: 0x${id} len: ${msg.len} data: ${msg.data}`);  
}))
