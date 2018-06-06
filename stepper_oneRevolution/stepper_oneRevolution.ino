
/*
 Stepper Motor Control - one revolution

 This program drives a unipolar or bipolar stepper motor.
 The motor is attached to digital pins 8 - 11 of the Arduino.

 The motor should revolve one revolution in one direction, then
 one revolution in the other direction.


 Created 11 Mar. 2007
 Modified 30 Nov. 2009
 by Tom Igoe

 */

#include <Stepper.h>

const int STEPS_PER_REVOLUTION = 1600;  // change this to fit the number of steps per revolution
                                        // for your motor
const int STEPPER_SPEED = 200;          // Stepper motot RPM

// One revolution of string ~= 2&3/8 inches linear, which translates to ~20 degrees of wheel turn

// initialize the stepper library on pins 8 through 11:
Stepper myStepper0(STEPS_PER_REVOLUTION, 3, 4);
Stepper myStepper1(STEPS_PER_REVOLUTION, 6, 7);

void setup() {
  // set the speed at 120 rpm:
  myStepper0.setSpeed(STEPPER_SPEED);
  myStepper1.setSpeed(STEPPER_SPEED);
  // pinMode(13, OUTPUT);             // Can be used with LED for debugging
  // initialize the serial port:
  Serial.begin(9600);
}

void loop() {
  if(Serial.available()){
    char message[3];
    // Serial.println("Hello World");
    Serial.readBytes(message, 3);
    if(message[0] == 76){         // Left == Counter Clock Wise
      double revolutions = (message[1] - 48)*10 + (message[2] - 48);
      revolutions = revolutions/50;
      step_counter_clockwise(revolutions*STEPS_PER_REVOLUTION*1.6); 
    }
    if(message[0] == 82){         // Right == Clock Wise
      double revolutions = (message[1] - 48)*10 + (message[2] - 48);
      revolutions = revolutions/50;
      step_clockwise(revolutions*STEPS_PER_REVOLUTION*1.6);
    }
  }
}

void step_clockwise(int steps){
  int i;
  int switch_step = steps/1.6;
  for(i = 0; i < switch_step; i++){
    myStepper0.step(-steps/switch_step);
    myStepper1.step(-steps/switch_step);
  }
}

void step_counter_clockwise(int steps){
  int i;
  int switch_step = steps/1.6;
  for(i = 0; i < switch_step; i++){
    myStepper0.step(steps/switch_step);
    myStepper1.step(steps/switch_step);
  }
}




