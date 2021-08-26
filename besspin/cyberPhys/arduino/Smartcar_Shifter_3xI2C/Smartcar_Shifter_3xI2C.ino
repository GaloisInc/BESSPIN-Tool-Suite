/*  Smartcar_Shifter_3xI2C.ino
 *  Project: CyberPhysical Demonstrator  
 *  Author: Kris Dobelstein
 *  Date: 20 November 2020
 *  
 *  Arduino Type: Teensy 3.6
 *  Clock speed: 120 MHz
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
 *  
 *  FlexCAN library is https://github.com/collin80/FlexCAN_Library
 */

#include <FlexCAN.h> // see note above regarding which FlexCAN library
#include <Wire.h>

#define PRINT(X) printCurrTime();Serial.print(X);Serial.print("\r\n");Serial2.print(X);Serial2.print("\r\n");

#define CHECK_I2C_BUS 1

byte data[5];
void toggle_led();
void printCurrTime(void);

#ifdef CHECK_I2C_BUS
unsigned int last_transaction_i2c0 = 0;
unsigned int last_transaction_i2c1 = 0;
unsigned int last_transaction_i2c2 = 0;
unsigned int max_i2c_trans_delay_ms = 500;
#endif

// Analog inputs
#define ANALOG_IN_BRAKE A15
#define ANALOG_IN_THROTTLE A14

// Master requesting data
void requestEvent_I2C0(void);
void requestEvent_I2C1(void);
void requestEvent_I2C2(void);

// Onboard LED
const int LED = 13;

// Digital communications constants
const unsigned int SERIAL_baud = 115200;
const unsigned short I2C_slave_address = 0x30;
const unsigned int I2C_frequency = 100000;
const unsigned int CAN_baud = 500000;

// CAN message decoder constants
const unsigned short shifter_CAN_ID = 0x230;    // a constant for the shifter's CAN ID
const unsigned char shifter_CAN_data_index = 0; // a constant for the shifter's gear selection data field

// global variables
volatile unsigned char shifter_gear = 0x28; // a variable for the shifter state
unsigned short brake_raw = 0;               // brake analog in
unsigned short throttle_raw = 0;            // throttle analog in

// Timer management
volatile unsigned long previous_poll_time = 25;
const unsigned int polling_interval = 20;

// debug message setting
const bool debug_msg_on = true;

FlexCAN Can0(CAN_baud, 0, 1, 1);
CAN_message_t CAN_msg;

/**
 * Print uptime in human readable format
 * "HH:MM:SS"
 */
void printCurrTime(void)
{
    static char buf[16] = {0};
    uint32_t n_ms = millis();
    uint32_t n_seconds = n_ms/1000;
    uint32_t n_minutes = n_seconds / 60;
    uint32_t n_hours = n_minutes / 60;

    n_seconds = n_seconds - n_minutes * 60;
    n_minutes = n_minutes - n_hours * 60;

    sprintf(buf, "(%02lu:%02lu:%02lu.%03lu) ", n_hours, n_minutes, n_seconds, n_ms);
    Serial.print(buf);
    Serial2.print(buf);
}

void setup()
{
  delay(1000);
  pinMode(LED, OUTPUT);
  // Activate a debug USB serial port
  Serial.begin(SERIAL_baud);
  Serial2.begin(SERIAL_baud);
  PRINT("Smart Fortwo shifter is online...");

  // Activate the CAN0 interface
  Can0.begin();

  // Enable I2C buses
  Wire.begin(I2C_slave_address);
  Wire.onRequest(requestEvent_I2C0);

  Wire1.begin(I2C_slave_address);
  Wire1.onRequest(requestEvent_I2C1);

  Wire2.begin(I2C_slave_address);
  Wire2.onRequest(requestEvent_I2C2);

  PRINT("Entering main loop...");
}

void toggle_led()
{
  static int val = 0;
  if (val)
  {
    digitalWrite(LED, HIGH);
    val = 0;
  }
  else
  {
    digitalWrite(LED, LOW);
    val = 1;
  }
}

static char printbuf[24] = {0};
unsigned int last_print_ms = 0;
unsigned int max_print_delay_ms = 1000; // Once a second
void loop()
{
  if ( (millis() - last_print_ms) >= max_print_delay_ms) {
    PRINT("I am alive");
    last_print_ms = millis();
  }
 
  if (Can0.available()) // this is non-blocking, returns number of available messages
  {
    Can0.read(CAN_msg);

    if (CAN_msg.id == shifter_CAN_ID)
    {
      shifter_gear = CAN_msg.buf[shifter_CAN_data_index];
      previous_poll_time = millis(); // capture the time of the last poll

      if (debug_msg_on)
      {
        // debug messages
        sprintf(printbuf, "shifter_gear: %#X", shifter_gear);
        PRINT(printbuf);
      }
    }
  }

  // Read analog values
  brake_raw = (unsigned short)analogRead(ANALOG_IN_BRAKE);
  if (debug_msg_on)
  {
    // debug messages
    sprintf(printbuf, "brake_raw: %u", brake_raw);
    PRINT(printbuf);
  }
  throttle_raw = (unsigned short)analogRead(ANALOG_IN_THROTTLE);

  if (debug_msg_on)
  {
    // debug messages
    sprintf(printbuf, "throttle_raw: %u", throttle_raw);
    PRINT(printbuf);
  }
  // data[0,1] = brake_raw
  // data[2,3] = throttle_raw
  // data[4] = gear
  memcpy(&data[0], &brake_raw, 2);
  memcpy(&data[2], &throttle_raw, 2);
  memcpy(&data[4], (const void *)&shifter_gear, 1);

  toggle_led();
  delay(50);

#ifdef CHECK_I2C_BUS
  // Check bus
  if (last_transaction_i2c0 > 0)
  {
    static int msg = 0;
    if (msg == 0) {
      PRINT("I2C0 received the first transaction");
      msg++;
    }
    if ((millis() - last_transaction_i2c0) >= max_i2c_trans_delay_ms)
    {
      PRINT("Reseting i2c0!");
      Wire.end();
      delay(10);
      Wire.begin(I2C_slave_address);
      Wire.onRequest(requestEvent_I2C0);
    }
  }

  if (last_transaction_i2c1 > 0)
  {
    static int msg = 0;
    if (msg == 0) {
      PRINT("I2C1 received the first transaction");
      msg++;
    }
    if ((millis() - last_transaction_i2c1) >= max_i2c_trans_delay_ms)
    {
      PRINT("Reseting i2c1!");
      Wire1.end();
      delay(10);
      Wire1.begin(I2C_slave_address);
      Wire1.onRequest(requestEvent_I2C1);
    }
  }

  if (last_transaction_i2c2 > 0)
  {
    static int msg = 0;
    if (msg == 0) {
      PRINT("I2C2 received the first transaction");
      msg++;
    }
    if ((millis() - last_transaction_i2c2) >= max_i2c_trans_delay_ms)
    {
      PRINT("Reseting i2c2!");
      Wire2.end();
      delay(10);
      Wire2.begin(I2C_slave_address);
      Wire2.onRequest(requestEvent_I2C2);
    }
  }
#endif
}

void requestEvent_I2C0(void)
{
#ifdef CHECK_I2C_BUS
  last_transaction_i2c0 = millis();
#endif
  Wire.write(data, 5);
}

void requestEvent_I2C1(void)
{
#ifdef CHECK_I2C_BUS
  last_transaction_i2c1 = millis();
#endif
  Wire1.write(data, 5);
}

void requestEvent_I2C2(void)
{
#ifdef CHECK_I2C_BUS
  last_transaction_i2c2 = millis();
#endif
  Wire2.write(data, 5);
}
