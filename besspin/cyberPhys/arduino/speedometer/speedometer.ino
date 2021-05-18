/*  speedometer.ino
 *  Project: SSITH CyberPhysical Demonstrator 
 *  Author: Kris Dobelstein
 *  Date: 18 August 2020
 *  
 *  Arduino Type: DIY Arduino Micro
 *  Stepper motor driver: https://www.pololu.com/product/2134
 *  Modified 2011 SmartForTwo Instrument Cluster Assembly #257-65361
 *  Baud Rate: 38400
 *  
 *  
 *  Microsteppping Resolution Truth Table
 *  M1 M0 Microstep Resolution  Excitation Mode
 *  --- --- --------------------  ---------------
 *  L   L   Full step             2 phase
 *  L   H   Half step             1-2 phase
 *  L   Z   Quarter step          W1-2 phase
 *  H   L   Eighth step           2W1-2 phase
 *  H   H   Sixteenth step        4W-1-2 phase
 *  H   Z   thirty-secondth Step  32
 *  
 */

// stepper motor driver pins
#define DRV8834_DIRECTION 8     // characterize per implementation
#define DRV8834_STEP 9          // low to high transition orders a step
#define DRV8834_nSLEEP 10        // logic level high to enable outputs
#define DRV8834_M0 13           // see truth table above
#define DRV8834_M1 5

#define BAUD_RATE 38400

// LED lighting
#define SPEEDO_NEEDLE_LIGHT 2
#define SPEEDO_NUMBER_LIGHT 3

// buttons
#define BUTTON_LEFT 0
#define BUTTON_RIGHT 1

#define INPUT_BUFFER 8

// Input management variables
String inputString ="";
bool stringComplete = false;

// stepper motor management variables
volatile short stepper_position = 0;
volatile unsigned short delay_micros = 300;
// proportional control constant.
// Larger values faster movement, more jerky
// Smaller values, slower movement, laggy
float kP = .25;

// speedometer management variables
// keep track of current output speed
volatile char current_speed_mph = 0;

// constants for stepper position to miles per hour mapping
const unsigned char speed_mph_max = 100;    // maximum speed on speedometer in mph
const float steps_per_mph = 9.7;  // steps per miles per hour at quarter steps                                          


void rotate(int steps){
  if (steps == 0) {
    //do nothing
  }
  else if (steps > 0) {
    while (steps > 0) {      
      //Serial.print("Steps left: ");
      //Serial.println(steps);
      digitalWrite(DRV8834_DIRECTION, LOW);
      digitalWrite(DRV8834_STEP, HIGH);
      delayMicroseconds(delay_micros);
      digitalWrite(DRV8834_STEP, LOW);
      delayMicroseconds(delay_micros);
      steps--;
      stepper_position++;
    }
  }
  else if (steps < 0) {
    while (steps < 0) {
      //Serial.print("Steps left: ");
      //Serial.println(steps);
      digitalWrite(DRV8834_DIRECTION, HIGH);
      digitalWrite(DRV8834_STEP, HIGH);
      delayMicroseconds(delay_micros);
      digitalWrite(DRV8834_STEP, LOW);
      delayMicroseconds(delay_micros);      
      steps++;
      stepper_position--;      
    }    
  }
  //Serial.println(stepper_position);
}

float speed_to_steps(float speed_mph) {
  if (speed_mph >= speed_mph_max) {
    // return steps_at_max_mph;
    return steps_per_mph * speed_mph_max;
  } 
  else if (speed_mph < 0) {
    return 0;
  } 
  else return speed_mph * steps_per_mph;  // maybe round this? @todo
}

short get_current_to_target_error(unsigned short target_position) {
  return target_position - stepper_position;
}

void config_full_steps(){
  digitalWrite(DRV8834_M1, LOW);
  digitalWrite(DRV8834_M0, LOW);
}

void config_half_steps(){
  digitalWrite(DRV8834_M1, LOW);
  digitalWrite(DRV8834_M0, HIGH);  
}

void config_quarter_steps(){
  digitalWrite(DRV8834_M1, LOW);
  pinMode(DRV8834_M0, INPUT);
}

void config_eighth_steps(){
  digitalWrite(DRV8834_M1, HIGH);
  digitalWrite(DRV8834_M0, LOW);
}

void config_sixteenth_steps(){
  digitalWrite(DRV8834_M1, HIGH);
  digitalWrite(DRV8834_M0, HIGH);
}

void enable_DRV8834(){
  digitalWrite(DRV8834_nSLEEP, HIGH);
}

void reset_speedometer_to_zero(){
  Serial.println("resetting to zero miles per hour");
  // move the needle counter-clockwise for a while so we know it "bottoms out" on the limiter
  rotate(-1400); // quarter steps
  delay(250);
  rotate(-20); // give it a little tickle to settle
  delay(10);
  // move the needle the emperically observed number of steps to zero from the limiter
  rotate(90); // quarter steps
  delay(100);
  // reset stepper_position to zero;
  zero_stepper_position();
  
}

void zero_stepper_position(){
  stepper_position = 0;
}

void setup() {
  // set up serial port and send a message about what we're doing
  Serial.begin(BAUD_RATE);
  inputString.reserve(INPUT_BUFFER);
  delay(1);
  Serial.println("Test routine for DRV8834 stepper motor driver...");
  delay(1);

  //Serial.println("Configuring pins...");
  // set up pins to interface with the DRV8834 module
  pinMode(DRV8834_DIRECTION, OUTPUT);
  pinMode(DRV8834_STEP, OUTPUT);
  pinMode(DRV8834_nSLEEP, OUTPUT);
  pinMode(DRV8834_M0, OUTPUT);
  pinMode(DRV8834_M1, OUTPUT);

  // configure speedometer LED control pins
  pinMode(SPEEDO_NEEDLE_LIGHT, OUTPUT);
  pinMode(SPEEDO_NUMBER_LIGHT, OUTPUT);  

  // Turn on the speedometer backlights
  digitalWrite(SPEEDO_NEEDLE_LIGHT, HIGH);
  digitalWrite(SPEEDO_NUMBER_LIGHT, HIGH); 

  pinMode(BUTTON_LEFT, INPUT_PULLUP);
  pinMode(BUTTON_RIGHT, INPUT_PULLUP);

  // enable the chip
  enable_DRV8834();
  delay(1); // let things settle
  
  // configure stepping resolution
  //config_half_steps();      // works ok
  config_quarter_steps();     // seems to be the best
  // config_eighth_steps();   // garbage
  // config_sixteenth_steps();// garbage

  // initialize the needle to zero miles per hour
  reset_speedometer_to_zero();  
}

void loop() {
  
  // poll the left button for a speedometer reset command
  if(digitalRead(BUTTON_LEFT) == LOW && current_speed_mph < 1) {
    Serial.println("LEFT");
    reset_speedometer_to_zero();
  }

  if(digitalRead(BUTTON_RIGHT) == LOW) {
    Serial.println("RIGHT");
  }
  
  if(stringComplete) {
    float speed_mph = inputString.toFloat();
    current_speed_mph = speed_mph;
    Serial.println(speed_mph);
    
    if (inputString.equals("r\n")) {
      reset_speedometer_to_zero();
    }
    
    if (inputString.equals("x\n")) {
      Serial.println("resetting stepper position");
      zero_stepper_position();      
    }        
    
    if (inputString.toFloat() > 0 or inputString.equals("0\n")) {
      float speed_mph = inputString.toFloat();
      //Serial.print("mph [received]: ");      
      //Serial.println(speed_mph);

      if (speed_mph < 0.1) {
        // go to zero position because it won't happen with proportional control
        if(stepper_position > 0) {
          rotate(stepper_position * -1);
        }
      }
      else {
        short error = get_current_to_target_error(speed_to_steps(speed_mph));
        rotate(error*kP);      
      }
    }
    inputString = "";         // reset the input string
    stringComplete = false;   // reset the stringComplete flag to false
  }
  serialEvent();  
}

// -----------------------------------------------
// SERIAL UART HARDWARE RX INTERRUPT ROUTINE
// -----------------------------------------------

void serialEvent() {
  while (Serial.available() ) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      char stringLength = inputString.length();
      stringComplete = true;
    }
  }  
}
