/*  Smartcar_Shifter.ino
 *  Project: CyberPhysical Demonstrator  
 *  Author: Kris Dobelstein
 *  Date: 27 October 2020
 *  
 *  Arduino Type: Teensy 3.2
 *  Clock speed: 72 MHz
 *  CAN Bus Transceiver: Texas Instruments TCAN332D
 *  
 *  The module running this sketch is only connected to the 
 *  Shifter assembly.
 *  
 *  Operational Notes
 *  
 *  1) Poll CAN buffer for messages at 50 Hz
 *  2) Update gear shifter state variable (i.e., shifter_gear)
 *  3) Share data via I2C when queried   
 */

#include <FlexCAN.h>
#include <i2c_t3.h>

// Function prototypes
void requestEvent(void);

// Digital communications constants
const unsigned int SERIAL_baud = 115200;
const unsigned short I2C_slave_address = 0x30;
const unsigned int I2C_frequency = 100000;  // need to double check frequency of I2C ADC
const unsigned int CAN_baud = 500000;

// CAN message decoder constants
const unsigned short shifter_CAN_ID = 0x230; // a constant for the shifter's CAN ID
const unsigned char shifter_CAN_data_index = 0; // a constant for the shifter's gear selection data field

// global variables
volatile unsigned int shifter_gear = 0; // a variable for the shifter state

// Timer management
volatile unsigned long previous_poll_time = 25;
const unsigned int polling_interval = 20;

// debug message setting
const bool debug_msg_on = false;

void setup() {
  
  // Activate a debug USB serial port
  Serial.begin(SERIAL_baud);
  Serial.println("Smart Fortwo shifter is online...");

  // Activate the CAN0 interface
  Can0.begin(CAN_baud);

  // Enable I2C bus
  Wire.begin(I2C_SLAVE, I2C_slave_address, I2C_PINS_18_19, I2C_PULLUP_EXT, I2C_frequency);
  Wire.onRequest(requestEvent);
  
  Serial.println("Entering main loop...");
}

void loop() {
  /*
   *  Main loop polls CAN controller buffer at ~50 Hz. Since the module is only intended
   *  to be connected to the shifter assembly, it only looks for messages sent from
   *  the shifter, which have ID 0x230. Relatively speaking, the shifter's mechanical
   *  state is updated far more slowly than 50 times, so we only care about the state of
   *  the shifter when it's polled or sampled. Testing has shown that this is sufficient.
   */
  if((millis() - previous_poll_time) >= polling_interval) {  
    CAN_message_t CAN_msg;
    
    if (Can0.available()) {
      Can0.read(CAN_msg);

      if (CAN_msg.id == shifter_CAN_ID) {
        shifter_gear = CAN_msg.buf[shifter_CAN_data_index];
        previous_poll_time = millis(); // capture the time of the last poll
        
        if (debug_msg_on) {
          // debug messages
          Serial.print(previous_poll_time); // print a timestamp
          Serial.print(" ");
          Serial.print(shifter_gear, HEX); // print the shifter gear state in hexadecimal
          Serial.println();
        }
      } 
    }
  }  
}

// interrupt service routine for outgoing I2C data
void requestEvent(void) {
  Wire.write(shifter_gear);
}
