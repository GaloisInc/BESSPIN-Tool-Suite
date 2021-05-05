import { SSL_OP_MICROSOFT_BIG_SSLV3_BUFFER } from 'constants';
import {createSocket} from 'dgram';
import ippkg from 'ip';
import { performance } from 'perf_hooks';
const broadcastAddr = ippkg.subnet(ippkg.address(),'255.255.255.0').broadcastAddress;

/**
 * CanListener
 *
 * Subscriber to CAN network messages
 *
 * @param {function} cb: Callable object to be notified with a CanMessage
 * @param {int32[]} can_ids: Array of CAN message IDs to subscribe to.
 *          undefined subscribes to all messages.
 */
class CanListener {
  constructor(cb, can_ids) {
    this.cb = cb;
    this.can_ids = can_ids;
  }

  // Returns true if the message is of interest to this listener.
  // A blank list of can_ids is treated like a subscribe-all
  interested(message_id) {
    if(this.can_ids == undefined || this.can_ids.length == 0) {
      return true;
    }
    return this.can_ids.includes(message_id);
  }
}

/**
 * CanMessage
 *
 * Represents a can message over the network
 *
 * id: CAN message ID
 * len: CAN message length in bytes
 * data[]: CAN bytes
 * timestamp: high resolution millisecond timestamp when message was recieved
 * 
 */
class CanMessage {
  constructor(raw) {
    this.id = this._unpack_id(raw);
    this.idString = "0x" + this.id.toString(16).toUpperCase();
    this.len = this._unpack_len(raw);
    this.data = this._unpack_data(raw, this.len);
    this._raw = raw;
    this._uint32 = this.getUint32();
    this._float = this.getFloat()
    this.timestamp = performance.now();
  }

   /**
   * Produce a CanMessage for a 4 byte float value
   *
   * @param {int32} id - CAN Message ID
   * @param {float32} char_val - Float value to send as data
   */
  static fromFloat(id, float_val) {
    this._raw = Buffer.alloc(9);
    this._raw.writeUInt32BE(id, 0); // id
    this._raw.writeUInt8(1, 4); // data length
    this._raw.writeFloatBE(float_val, 5); // data
    return new CanMessage(data);
  }

  /**
   * Produce a CanMessage for a single char value
   *
   * @param {int32} id - CAN Message ID
   * @param {uint8} char_val - Character value to send as data
   */
  static fromChar(id, char_val) {
    let data = Buffer.alloc(6);
    data.writeUInt32BE(id, 0); // id
    data.writeUInt8(1, 4); // data length
    data.writeUInt8(char_val, 5); // data
    return new CanMessage(data);
  }

  buffer() {
    return this._raw;
  }

  // Converts first four bytes of data to an uint32 value
  getUint32() {
    let binary = new Uint8Array([this._raw[5], this._raw[6], this._raw[7], this._raw[8]]);
    let dv = new DataView(binary.buffer);
    return dv.getUint32();
  }

  // Converts first four bytes of data to a float
  getFloat() {
    let binary = new Uint8Array([this._raw[5], this._raw[6], this._raw[7], this._raw[8]]);
    let dv = new DataView(binary.buffer);
    return dv.getFloat32(0);
  }

  _unpack_id(buffer) {
    let binary = new Uint8Array([buffer[0], buffer[1], buffer[2], buffer[3]]);
    let dv = new DataView(binary.buffer);
    return dv.getUint32();
  }

  _unpack_len(buffer) {
    return buffer[4];
  }

  _unpack_data(buffer, len) {
    var out = [];
      for(let i=0; i<len; i++) {
        out.push(buffer[5 + i].toString(16));
    }
    return out;
  }
}

/**
 * CanNetwork
 * 
 * CAN Network. Manages routing of CanMessages to CanListeners
 * 
 * listeners[]: Array of CanListener objects
 * port: UDP Port
 * ip: broadcast IP
 * client: UDP socket object
 * 
 */
class CanNetwork {
    

    constructor(port) {
        this.listeners = []
        this.port = port;
        this.ip = broadcastAddr;
        this.client = createSocket('udp4');

        this.client.on('error', (err) => {
            console.log(`client error:\n${err.stack}`);
            this.client.close();
          });
          
        this.client.on('message', (raw_msg, rinfo) => {
            for(let l of this.listeners) {
              let can_msg = new CanMessage(raw_msg);
              // Send message to listeners
              if(l.interested(can_msg.id)) {
                l.cb(can_msg);
              }
            }
        });
          
        this.client.on('listening', () => {
            this.client.setBroadcast(true);
            console.log(`client listening ${broadcastAddr}:${this.port}`);
        });
          
        this.client.bind(this.port, () => {
          console.debug(`Bound to port ${this.port}`);
        });
    
    }

    // Send a CAN message over the network to our registered port 
    send(buffer) {
      send_to_port(buffer, this.port);
    }

    // send a CAN message over the network to a specified port
    send_to_port(buffer, dport) {
      this.client.send(buffer, dport, this.ip);
    }
    
    // Register a CanListener with the network
    register(listener) {
      console.info("Registering listener on port " + this.port);
      this.listeners.push(listener);
    }

    // Unregister a CanListener from the network
    unregister(listener) {
      this.listeners.splice(this.listeners.indexOf(listener), 1);
    }
}


const CANID = {
  CAN_ID_CAR_X: 0XAAFEAAC1,
  CAN_ID_CAR_Y: 0XAAFEADF6,
  CAN_ID_CAR_Z: 0XAAFEAABF,
  CAN_ID_CAR_R: 0XAACDAD11,  
  CAN_ID_GEAR: 0XAAF01000,
  CAN_ID_THROTTLE: 0XAAF01A00,
  CAN_ID_BRAKE: 0XAAF01B00,
  CAN_ID_STEERING: 0XAAF01D00,
  CAN_ID_BUTTON_PRESSED: 0XAAFECA00

}

export {
  CanNetwork,
  CanMessage,
  CanListener,
  CANID
}
