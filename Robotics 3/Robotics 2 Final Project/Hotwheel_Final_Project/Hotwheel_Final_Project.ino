// Natasha Sieh and Samuel Thai
// 1/11/23
// Robotics 2
// This program is used to spin a stepper motor based on each step of the rotary encoder. These values end up displaying on an LCD.
#include <Arduino.h>
#include <Wire.h>
#include <Encoder.h>
#include <LiquidCrystal_I2C.h>
#include "BasicStepperDriver.h"
// Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MOTOR_STEPS 200
#define RPM 120
#define MICROSTEPS 1
 
// All the wires needed for full functionality of stepper motor
#define DIR 5
#define STEP 6
int x = 0;
 
BasicStepperDriver stepper(MOTOR_STEPS, DIR, STEP);
int circleguy=50; //sets circle guy as a degree of rotation for stepper rotate code
int Switch; //sets a seperate integer for the state of the switch
 
 
// Rotary encoder with Arduino to print position and direction of rotation
#include <LiquidCrystal_I2C.h>
#define outputA 2
#define outputB 3
#define Switch 4 // defines the digital pin that is connected to the switch
Encoder myEnc(2, 3); // defines which rotation that it goes
// Initialize the LCD library with I2C address and LCD size
LiquidCrystal_I2C lcd (0x27, 16, 2);
int printed = 0; // checking if the print is displayed
int counter = 0;
int newPosition;
int oldPosition;
// direction is clockwise (CW) or countr clock wise (CCW)
String currentDir = "";
 
void setup() {
 
 // Setup Serial Monitor
 Serial.begin(9600);
 // Set encoder pins as inputs
 pinMode(2,INPUT);
 pinMode(3,INPUT);
 pinMode(4,INPUT);
  lcd. init ();
// Turn on the backlight on LCD.
 lcd. backlight ();
 lcd. setCursor (1, 1);
 lcd.print ("ROTARY ENCODER");
 delay(1000);
 lcd.clear();
 lcd.setCursor(0, 0);
 lcd.print("Rotate the knob");
  // Read the initial state of outputA
 oldPosition = digitalRead(2);
 
 // stepper motor
 stepper.begin(MOTOR_STEPS);  // starts the stepper
 stepper.rotate(x); // starts the stepper at a position of zero
 
}
void loop() {
 // Read the current state of outputA
 newPosition = digitalRead(2);
 // If last and current state of outputA are different, then pulse occurred
 // React to only 1 state change to avoid double count
 if (newPosition != oldPosition  && newPosition == 1)
 {
   // If the outputB state is different than the outputA state then
   // the encoder is rotating CCW so decrement
   if (digitalRead(3) != newPosition)
   {
     counter ++;
     currentDir ="CW";
   }
   else
   {
     // Encoder is rotating CW so increment
     counter --;
     currentDir ="CCW";
   }
 
   Serial.print("Direction: ");
   Serial.print(currentDir);
   Serial.print(" | Counter: ");
   Serial.println(counter);
   lcd.clear();
   lcd.setCursor(0, 0);
   lcd.print("Position: ");
   lcd.setCursor(10, 0);
   lcd.print(counter);
   lcd.setCursor(0, 1);
   lcd.print("Dir: ");
   lcd.setCursor(5, 1);
   lcd.print(currentDir);
 
// rotating CCW when the rotary encoder is turned leftwards
   if (currentDir == "CCW")
   {
    stepper.rotate(146);
   }
 
   if (currentDir == "CW")
   {
    stepper.rotate(-146);
   }
 }
 
 // Remember last outputA state
 oldPosition = newPosition;
 button(); 
 }
 
void button() {
 //Read the button state
   int buttonState = digitalRead(Switch); // reads the button state value if it is LOW or HIGH
   if (buttonState == LOW)
   {
   Serial.println("Button pressed!"); // says that the button is pressed when the button state is LOW
   counter = 0;
   //lcd.setCursor(10, 0); // value of the position
   //lcd.print(counter); // function that sets the encoder position to zero when the button is low or pressed
   lcd.clear();
   lcd.setCursor(0, 0);
   lcd.print("Position: ");
   lcd.setCursor(10, 0);
   lcd.print(counter);
   lcd.setCursor(0, 1);
   lcd.print("Dir: ");
   lcd.setCursor(5, 1);
   lcd.print(currentDir);
   // add code for stopping the stepper motor when the button is pressed
 //debounce switch press 
     while (!digitalRead(Switch)) // while the switch is LOW
    {
      // set the LCD position value to zero
       myEnc.write(0);
       stepper.rotate(180);
    }

// Homing
    if (x == 90)
    {
      // homing position is 90 from starting position
      stepper.rotate(-146);
    }

    else if (x == 180)
    {
      // homing position is 180 from starting position
      stepper.rotate(-146);
      stepper.rotate(-146);
    }

    else if (x == 270)
    {
      // homing position is 270 from starting position
      stepper.rotate(146);
    }
   }
}
