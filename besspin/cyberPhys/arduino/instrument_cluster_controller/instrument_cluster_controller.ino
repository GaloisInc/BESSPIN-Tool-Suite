/*  instrument_cluster_controller.ino
 *  Project: CyberPhysical Demonstrator  
 *  Contributors: 
 *    Kris Dobelstein <kris.dobelstein@agilehardwarenwllc.com>
 *    Ethan Lew <elew@galois.com>
 *  Date: 11/04/2020
 *  
 *  Arduino Type: Teensy 3.2
 *  Clock speed: 72 MHz
 *  CAN Bus Transceiver: Texas Instruments TCAN332D
 *  
 *  Shows up as "USB Serial Device" in Windows Device Manager
 *  
 *  To Do:
 *  1) debounce neutral between gear shifts
 *   
 */

#include <FlexCAN.h>
#include <TeensyThreads.h>

// structure from Python BeamNG management ecosystem
typedef struct {
  float wheelspeed_mph; // used
  float fuel_percent; // used
  float throttle_percent; // not used, but verified
  char gear_state; // used
  unsigned char oil; // not used, not verified
  unsigned char parking_brake; // used
  unsigned char highbeam; // not used
  unsigned char headlights; // 0 = off, 1 = headlights, 2 = high beams  
  bool right_signal; // used
  bool left_signal; // used
  bool esc_active; // used  
  bool abs_active; // used
  bool brake_lights; // works
} beamng_data;

// car_data packet to be populated
beamng_data beamng_vehicle;

// debug serial port
const unsigned int SERIAL_baud = 115200;

// CAN bus setup
const unsigned int CAN_baud = 500000;

// CAN bus messages necessary to control the instrument cluster
CAN_message_t tx_msg_0x1E1; // seat belt sensor, airbag sensor
CAN_message_t tx_msg_0x200; // speedometer!
CAN_message_t tx_msg_0x210; // turns off a bunch of warnings
CAN_message_t tx_msg_0x308; // fuel level, coolant temperature, battery warning, oil warning, CEL warning
CAN_message_t tx_msg_0x418; // transmission
CAN_message_t tx_msg_0x423; // main instrument cluster control and headlights

// Smart Fortwo speedometer calibration
const float steps_per_mph = 29.52;

// Smart Fortwo fuel capacity and calibration
const float fuel_capacity_gals = 8.7;
const float ticks_per_gallon = 52.64;
const short fuel_offset = 309;

// instrument cluster gears
const unsigned char msg_0x418_D0_gear_park = 0x50;
const unsigned char msg_0x418_D0_gear_reverse = 0x52;
const unsigned char msg_0x418_D0_gear_neutral = 0x4E;
const unsigned char msg_0x418_D0_gear_drive = 0x0B;
const unsigned char msg_0x418_D0_gear_first = 0x31;
const unsigned char msg_0x418_D0_gear_second = 0x32;
const unsigned char msg_0x418_D0_gear_third = 0x33;
const unsigned char msg_0x418_D0_gear_fourth = 0x34;
const unsigned char msg_0x418_D0_gear_fifth = 0x35;

// beamng gears
// there doesn't seem to be a park gear in their docs
const unsigned char beamng_gear_reverse = 0xFF;
const unsigned char beamng_gear_neutral = 0x00;
const unsigned char beamng_gear_first = 0x01;
const unsigned char beamng_gear_second = 0x02;
const unsigned char beamng_gear_third = 0x03;
const unsigned char beamng_gear_fourth = 0x04;
const unsigned char beamng_gear_fifth = 0x05;
const unsigned char beamng_gear_sixth = 0x06;
const unsigned char beamng_gear_seventh = 0x07;
const unsigned char beamng_gear_eighth = 0x08;

// instrument cluster indicator lamps in 0x200
const unsigned char msg_0x200_D1_indicators_off = 0x00;
const unsigned char msg_0x200_D1_parking_brake_on = 0x02;
const unsigned char msg_0x200_D1_abs_active = 0x04;
const unsigned char msg_0x200_D1_esc_active = 0x20;

// instrument cluster indicator lamps in 0x423
volatile bool turn_signals_active = false;
const long turn_signal_delay = 400;
const unsigned char msg_0x423_D1_speedometer_backlight_on = 0x08;  // turns on speedometer backlight
const unsigned char msg_0x423_D1_highbeams = 0x04;
const unsigned char msg_0x423_D1_left_turn_signal = 0x02;
const unsigned char msg_0x423_D1_right_turn_signal = 0x01;
const unsigned char msg_0x423_D3_lowbeams = 0x01;
const unsigned char msg_0x423_D3_speedometer_backlight_on = 0x02;

volatile byte speed_bytes[2];
volatile byte fuel_bytes[2]; // by default, set to full

// various time-related variables
const unsigned int buzz_delay = 7000; // the speedometer has to bottom out at startup
const unsigned int reset_to_default_limit = 3000; // how long to wait until resetting
volatile unsigned int reset_to_default_counter = 0;
volatile unsigned long previous_tx_time_20ms = 25;  // keep track of time for tx msgs

// car lights
#define LEFT_TURN_SIGNAL A0
#define RIGHT_TURN_SIGNAL A1
#define BRAKE_LIGHT_R 10
#define BRAKE_LIGHT_L 9

void set_speedometer(float speed_mph) {
    /*
     *  converts a float to a short and then populates the applicable
     *  buffers in message 0x200 to drive the speedometer needle
     */
    if (speed_mph >= 0.0) {
    short steps = short(speed_mph * (steps_per_mph));
    speed_bytes[0] = steps>>8;
    speed_bytes[1] = steps & 0xFF;
  }
    // populate msg 0x200 with latest values
    tx_msg_0x200.buf[2] = speed_bytes[0]; // SPEEDOMETER CONTROL
    tx_msg_0x200.buf[3] = speed_bytes[1]; // SPEEDOMETER CONTROL
    tx_msg_0x200.buf[4] = speed_bytes[0]; // SPEEDOMETER CONTROL
    tx_msg_0x200.buf[5] = speed_bytes[1]; // SPEEDOMETER CONTROL
    tx_msg_0x200.buf[6] = speed_bytes[0]; // SPEEDOMETER CONTROL
    tx_msg_0x200.buf[7] = speed_bytes[1]; // SPEEDOMETER CONTROL    
}

void set_fuel_level(float fuel_percent) {
    /*
     *  converts a float between 0.0 and 1.0 to a short and then populates the applicable
     *  buffers in msg 0x308 to set the fuel level blips on the multifunction display
     */  
  if (fuel_percent >=0.0 && fuel_percent <=1.0) {
    short ticks = short(((fuel_capacity_gals * (1.0 - fuel_percent))*ticks_per_gallon)+fuel_offset);
    // update fuel message with latest values
    tx_msg_0x308.buf[6] = ticks>>8;
    tx_msg_0x308.buf[7] = ticks & 0xFF;    
  }    
}

unsigned char convert_gear_state_for_mfd(char gear) {
  /*
   *  convert the value that BeamNG sends into the value
   *  that drives the Smart Fortwo's gear state character
   *  on the multifunction display (MFD)
   *  
   *  Smart Fortwo MFD can display P, R, N, 1-5
   */
  switch (gear) {
    case beamng_gear_reverse:
      return msg_0x418_D0_gear_reverse;
      break;
    case beamng_gear_neutral:
      return msg_0x418_D0_gear_neutral;
      break;
    case beamng_gear_first:
      return msg_0x418_D0_gear_first;
      break;
    case beamng_gear_second:
      return msg_0x418_D0_gear_second;
      break;
    case beamng_gear_third:
      return msg_0x418_D0_gear_third;
      break;
    case beamng_gear_fourth:
      return msg_0x418_D0_gear_fourth;
      break;
    case beamng_gear_fifth:      
      return msg_0x418_D0_gear_fifth;
      break;
    case beamng_gear_sixth:
      // Smart Fortwo instrument cluster cannot display
      // higher than fifth gear      
      return msg_0x418_D0_gear_fifth;
      break;
    case beamng_gear_seventh:      
      return msg_0x418_D0_gear_fifth;
      break;
    case beamng_gear_eighth:      
      return msg_0x418_D0_gear_fifth;
      break;      
    default:
      // assume nothing, so park?      
      return msg_0x418_D0_gear_park;
  }
}

unsigned char get_indicator_lamp_states_0x200(unsigned char parking_brake, unsigned char abs_active, unsigned char esc_active) {
  /*
   *  Form the indicator lamp byte for 0x200, D1
   */

  return msg_0x200_D1_indicators_off 
         | (parking_brake * msg_0x200_D1_parking_brake_on) 
         | (abs_active * msg_0x200_D1_abs_active) 
         | (esc_active * msg_0x200_D1_esc_active); 
}

void toggle_headlight_state(unsigned char headlights) {
  // get current state of object items that contain headlight bits
  unsigned char temp_byte_0x423_D1 = tx_msg_0x423.buf[1];
  unsigned char temp_byte_0x423_D3 = tx_msg_0x423.buf[3];

  // low beams on
  if (headlights == 0) {
    tx_msg_0x423.buf[1] = (temp_byte_0x423_D1 & 0b11111011) | msg_0x423_D1_speedometer_backlight_on; // AND it with inverse of highbeams on to reset the highbeams bit
    tx_msg_0x423.buf[3] = (temp_byte_0x423_D3 & 0b11111110) | msg_0x423_D3_speedometer_backlight_on; // AND it with inverse of lowbeams on to reset the lowbeams bit
    //digitalWrite(LEFT_TURN_SIGNAL, LOW);
    //digitalWrite(RIGHT_TURN_SIGNAL, LOW);
  }
  else if (headlights == 1) {    
    tx_msg_0x423.buf[3] = temp_byte_0x423_D3 | msg_0x423_D3_lowbeams;
    //digitalWrite(LEFT_TURN_SIGNAL, HIGH);
    //digitalWrite(13, HIGH);
  }
  else if (headlights == 2) {
    tx_msg_0x423.buf[1] = temp_byte_0x423_D1 | msg_0x423_D1_highbeams;
    //digitalWrite(RIGHT_TURN_SIGNAL, HIGH);
  }
}

void brake_lights_state(bool state) {
  if (state == true) {
    digitalWrite(BRAKE_LIGHT_L, HIGH);
    digitalWrite(BRAKE_LIGHT_R, HIGH);
  }
  if (state == false) {
    digitalWrite(BRAKE_LIGHT_L, LOW);
    digitalWrite(BRAKE_LIGHT_R, LOW);    
  }
}

void blink_signal() {  
  /*
   *  Free running thread that "blinks" the turn signals on or off
   *  depending on the state of .left_signal or .right_signal.
   */
  while(1) {   
    //unsigned char temp_byte_0x423_D1 = tx_msg_0x423.buf[1]; 
    digitalWrite(LEFT_TURN_SIGNAL, LOW);
    digitalWrite(RIGHT_TURN_SIGNAL, LOW);
    tx_msg_0x423.buf[1] = (tx_msg_0x423.buf[1] & 0b11111100)
                          | msg_0x423_D1_speedometer_backlight_on;
    threads.delay(turn_signal_delay);
    
    if (beamng_vehicle.left_signal == 1) {digitalWrite(LEFT_TURN_SIGNAL, HIGH);}
    if (beamng_vehicle.right_signal == 1) {digitalWrite(RIGHT_TURN_SIGNAL, HIGH);}
    
    tx_msg_0x423.buf[1] = tx_msg_0x423.buf[1]
                          | (msg_0x423_D1_left_turn_signal * beamng_vehicle.left_signal) 
                          | (msg_0x423_D1_right_turn_signal * beamng_vehicle.right_signal)
                          | msg_0x423_D1_speedometer_backlight_on;
    threads.delay(turn_signal_delay);
  }
}

void setup() {
 
  // Activate a debug USB serial port
  Serial.setTimeout(1);
  Serial.begin(SERIAL_baud);
  //inputString.reserve(10);
  Serial.println("Smart Fortwo instrument cluster is online...");

  // Activate the CAN0 interface
  //FlexCAN CANTransmitter(CAN_baud);
  Can0.begin(CAN_baud);

  // init msg 0x1E1
  // turns off seat belt sensor, airbag sensor
  tx_msg_0x1E1.ext = 0;
  tx_msg_0x1E1.id = 0x1E1;
  tx_msg_0x1E1.len = 8;
  tx_msg_0x1E1.buf[0] = 0x00;
  tx_msg_0x1E1.buf[1] = 0x00;
  tx_msg_0x1E1.buf[2] = 0x00;
  tx_msg_0x1E1.buf[3] = 0x00;
  tx_msg_0x1E1.buf[4] = 0x00;
  tx_msg_0x1E1.buf[5] = 0x00;
  tx_msg_0x1E1.buf[6] = 0x00;
  tx_msg_0x1E1.buf[7] = 0x00; 

  // init msg 0x200
  // turns off parking brake lamp, ABS lamp, ESC lamp
  // sets speedometer to zero
  tx_msg_0x200.ext = 0;
  tx_msg_0x200.id = 0x200;
  tx_msg_0x200.len = 8;
  tx_msg_0x200.buf[0] = 0x00;
  tx_msg_0x200.buf[1] = 0x00;
  set_speedometer(0.0);

  // init msg 0x210  
  // Necessary to turn off most warning lights
  // Nothing in this message changes
  tx_msg_0x210.ext = 0;
  tx_msg_0x210.id = 0x210;
  tx_msg_0x210.len = 8;
  tx_msg_0x210.buf[0] = 0x00;
  tx_msg_0x210.buf[1] = 0x00;
  tx_msg_0x210.buf[2] = 0x00;
  tx_msg_0x210.buf[3] = 0x40; // 0x40 is best config here as it turns off most warning lights
  tx_msg_0x210.buf[4] = 0x00;
  tx_msg_0x210.buf[5] = 0x00;  
  tx_msg_0x210.buf[6] = 0x00;
  tx_msg_0x210.buf[7] = 0x00;    

  // init msg 0x308
  // turns off battery, oil and CEL warning lamps
  // sets fuel level to 100%
  tx_msg_0x308.ext = 0;
  tx_msg_0x308.id = 0x308;
  tx_msg_0x308.len = 8;
  tx_msg_0x308.buf[0] = 0x00;
  tx_msg_0x308.buf[1] = 0x00;
  tx_msg_0x308.buf[2] = 0x00;
  tx_msg_0x308.buf[3] = 0x00;
  tx_msg_0x308.buf[4] = 0x00;
  tx_msg_0x308.buf[5] = 0x00;
  set_fuel_level(1.0);

  // init msg 0x418
  // sets transmission to park
  tx_msg_0x418.ext = 0;
  tx_msg_0x418.id = 0x418;
  tx_msg_0x418.len = 8;
  tx_msg_0x418.buf[0] = msg_0x418_D0_gear_park; // initialize in park
  tx_msg_0x418.buf[1] = 0x00; // logs show possible values of 0xFE, but 0x00 still works
  tx_msg_0x418.buf[2] = 0x00; // ? a5
  tx_msg_0x418.buf[3] = 0x00; // ? 56
  tx_msg_0x418.buf[4] = 0x00; // ? 10
  tx_msg_0x418.buf[5] = 0x00; // ? 00
  tx_msg_0x418.buf[6] = 0x00; // ? 00
  tx_msg_0x418.buf[7] = 0x00; // ? 00     

  // init msg 0x423
  //instrument cluster  
  tx_msg_0x423.ext = 0;
  tx_msg_0x423.id = 0x423; // the instrument cluster
  tx_msg_0x423.len = 7;
  tx_msg_0x423.buf[0] = 0x01; // key in ignition and running
  tx_msg_0x423.buf[1] = msg_0x423_D1_speedometer_backlight_on; // always leave 0x08, don't clobber 0x04 w/ blinker thread
  tx_msg_0x423.buf[2] = 0x00;
  tx_msg_0x423.buf[3] = msg_0x423_D3_speedometer_backlight_on; 
  tx_msg_0x423.buf[4] = 0x00;
  tx_msg_0x423.buf[5] = 0x00;
  tx_msg_0x423.buf[6] = 0x00;    

  delay(buzz_delay);  // let the instrument cluster self-cal the speedometer needle

  pinMode(LEFT_TURN_SIGNAL, OUTPUT);
  digitalWrite(LEFT_TURN_SIGNAL, HIGH);
  pinMode(RIGHT_TURN_SIGNAL, OUTPUT);
  digitalWrite(RIGHT_TURN_SIGNAL, HIGH);
  pinMode(BRAKE_LIGHT_R, OUTPUT);
  digitalWrite(BRAKE_LIGHT_R, HIGH);
  pinMode(BRAKE_LIGHT_L, OUTPUT);
  digitalWrite(BRAKE_LIGHT_L, HIGH);  

  delay(2000);
  digitalWrite(BRAKE_LIGHT_R, LOW);
  digitalWrite(BRAKE_LIGHT_L, LOW);

  // initialize the car_data packet bng
  memset((void *)&beamng_vehicle, 0, sizeof(beamng_data));

  // start the signal blinking thread
  threads.addThread(blink_signal);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  if ( (millis() - previous_tx_time_20ms) >= 20) {
    
    // broadcast CAN messages every 20 ms
    Can0.write(tx_msg_0x423); // instrument cluster
    Can0.write(tx_msg_0x1E1); // seat belt warning, airbag sensor warning
    Can0.write(tx_msg_0x200); // parking brake, ABS light, ESC light, speedometer
    Can0.write(tx_msg_0x210); // keep various warnings cleared
    Can0.write(tx_msg_0x308); // fuel level, coolant temperature
    Can0.write(tx_msg_0x418); // transmission

    previous_tx_time_20ms = millis();
  }   

  if ( millis() - reset_to_default_counter >= reset_to_default_limit ) {
    // if we haven't received anything in a while, reset the instrument cluster
    
    // reset speedometer to zero
    set_speedometer(0.0);

    // reset the fuel level
    set_fuel_level(1.0);
    
    // reset gear state to park
    tx_msg_0x418.buf[0] = msg_0x418_D0_gear_park;  

    // reset values
    beamng_vehicle.throttle_percent = 0; // not used, but verified
    beamng_vehicle.parking_brake = 0; // used
    beamng_vehicle.headlights = 0; // 0 = off, 1 = headlights, 2 = high beams
    beamng_vehicle.right_signal = 0; // used
    beamng_vehicle.left_signal = 0; // used
    beamng_vehicle.esc_active = 0; // used
    beamng_vehicle.abs_active = 0; // used 

    // reset indicator lamps based on above values
    tx_msg_0x200.buf[0] = get_indicator_lamp_states_0x200(beamng_vehicle.parking_brake, 
                          beamng_vehicle.abs_active, beamng_vehicle.esc_active); 
    
    // reset headlights based on above value                           
    toggle_headlight_state(beamng_vehicle.headlights); 

    // turn off the brake light
    digitalWrite(BRAKE_LIGHT_R, LOW);
    digitalWrite(BRAKE_LIGHT_L, LOW);
  }
}

void serialEvent() {
  if (Serial.available()) {
    // get the new character:    
    Serial.readBytes((char*)&beamng_vehicle, sizeof(beamng_data));  

    //Serial.print("mph: ");
    //Serial.print(beamng_vehicle.wheelspeed_mph);
    //Serial.println();
    
    // update the speedometer's indicated speed
    set_speedometer(beamng_vehicle.wheelspeed_mph);

    // update fuel level
    set_fuel_level(beamng_vehicle.fuel_percent); 

    // update the gear on the multifunction display
    tx_msg_0x418.buf[0] = convert_gear_state_for_mfd(beamng_vehicle.gear_state);

    // update the indicator lamps in msg 0x200
    tx_msg_0x200.buf[0] = get_indicator_lamp_states_0x200(beamng_vehicle.parking_brake, 
                          beamng_vehicle.abs_active, beamng_vehicle.esc_active);

    // update the headlights indicator lamp in 0x423
    toggle_headlight_state(beamng_vehicle.headlights);

    // toggle brake lights
    if (beamng_vehicle.brake_lights == 1) {
      digitalWrite(BRAKE_LIGHT_R, HIGH);
      digitalWrite(BRAKE_LIGHT_L, HIGH);
    }
    else {
      digitalWrite(BRAKE_LIGHT_R, LOW);
      digitalWrite(BRAKE_LIGHT_L, LOW);
    }

    reset_to_default_counter = millis(); 
    }
}
