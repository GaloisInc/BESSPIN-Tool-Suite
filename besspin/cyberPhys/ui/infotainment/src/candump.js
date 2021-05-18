
// Project: SSITH CyberPhysical Demonstrator
// Name: candump.js
// Author: Steven Osborn <steven@lolsborn.com>
// Date: 1 December 2020

// Dumps all CAN traffic on CyberPhys network to stdout

const PORT = 5085
const dgram = require('dgram');
const ip = require('ip');
const client = dgram.createSocket('udp4');
const broadcastAddr = ip.subnet(ip.address(),'255.255.255.0').broadcastAddress

let unpack_id = (buffer) => {
  var binary = buffer[0];
  binary |= buffer[1] << 8;
  binary |= buffer[2] << 16;
  binary |= buffer[3] << 24;
  return binary;
}
let unpack_len = (buffer) => {
  var binary = buffer[4];
  return binary;
}
let unpack_data = (buffer, len) => {
  var out = [];
  for(let i=0; i<len; i++) {
    out.push(buffer[5 + i].toString(16));
  }
  return out;
}

client.on('error', (err) => {
  console.log(`client error:\n${err.stack}`);
  client.close();
});

client.on('message', (msg, rinfo) => {
  let msg_id = unpack_id(msg);
  let msg_len = unpack_len(msg);
  let msg_data = unpack_data(msg, msg_len);
  console.log(`id: ${msg_id} len: ${msg_len} data: ${msg_data} from: ${rinfo.address}:${rinfo.port}`); 
});

client.on('listening', () => {
  client.setBroadcast(true);
  client.setMulticastTTL(128); 
  console.log(`client listening ${broadcastAddr}:${PORT}`);
});

client.bind(PORT, () => {
  client.setMulticastInterface(broadcastAddr);
});