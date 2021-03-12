#include <Bounce2.h>

Bounce b = Bounce();

void setup() {
  // put your setup code here, to run once:
  b.attach(14, INPUT);
  b.interval(0);
}

void loop() {
  b.update();
  if(b.fell()) {
    Keyboard.set_modifier(MODIFIERKEY_CTRL);
    Keyboard.send_now();
    Keyboard.set_key1(KEY_F7);
    Keyboard.send_now();
    delay(300);
    Keyboard.set_modifier(0);
    Keyboard.set_key1(0);
    Keyboard.send_now();
  }
}
