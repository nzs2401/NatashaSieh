// Robotics 3
// Date: 2/##/23
// Natasha Sieh
// Description:
/* This code uses a button, ESC, and brushless motor.
 * The button is used to initialize the start sequence.
 * Once the button is clicked, the speed of the brushless motor increases from 1000 to its max, 2000, for a total of 7 seconds.
 * Once the 7 seconds is done, the brushless motor will break (speed will be 1000) so that the propeller can launch up into the air. */
#include <Servo.h> // starts the Servo library


Servo ESC; // create servo object to control the ESC
int button = 3; // defines the button at pin 3
int period = 1000; // 1000ms = 1 second
const unsigned long event_1 = 6000; // change if needed // increase speed of motor for total of 6 seconds
unsigned long previousTime = 0;
int minPulse = 700;
int maxPulse = 2000;
int speedChange = 12; // change if needed
int speed = minPulse;
int clicked = 0;
int duration = 0;

void setup() {
   pinMode(button, INPUT_PULLUP); // says that the button is an input pullup which monitors the state of a button
   ESC.attach(9,minPulse,maxPulse); // (digital pin 9,min pulse width of 700 microseconds,max pulse width of 2000 microseconds
   ESC.writeMicroseconds(minPulse); // sets the speed of the ESC to 700 (its minimum)
   Serial.begin(9600); // starts the serial monitor
}


// speed_controller
void speed_controller()  { // function called speed_controller
   int buttonstate = digitalRead(button); // reads button state
   //Serial.println("buttonstate");
   //Serial.println(buttonstate);
   if (buttonstate == 0)
   { // if button is clicked, then initialize start sequence
       Serial.println("Clicked!"); // print in the serial monitor that the button was clicked
       clicked = 1; // clicked once
   }


   if (clicked == 1)
   {
       unsigned long currentTime = millis(); // sets time
       previousTime = currentTime; // initial time of acceleration
       Serial.println("currentTime1:");
       Serial.println(currentTime);


       do
       {
            // speed starts at 700, then slowly increases to 2000 by speedChange increments
           if (speed < maxPulse)
           {// if speed is less than 2000
               Serial.println("Speed: "); // prints the speed in serial monitor
               Serial.println(speed); // prints the speed in serial monitor
               ESC.writeMicroseconds(speed); // the ESC's speed will be accelerating at a SpeedChange rate
               speed = speed + speedChange; // speed increments
           }
           Serial.println("Speed: "); // prints the speed in serial monitor
           Serial.println(speed); // prints the speed in serial monitor
           currentTime = millis(); // reads where the current time is
          
           duration = currentTime - previousTime;
           Serial.println("Duration:");
           Serial.println(duration);
          
       } while (currentTime - previousTime < event_1);
           Serial.println("Stop");
           ESC.writeMicroseconds(700); // figure out how to stop
           clicked = 0;
           speed = minPulse; // only if you want the program to run every time your press button
      
   }
      
}


void loop() {
   speed_controller(); // run the function called speed_controller
}
