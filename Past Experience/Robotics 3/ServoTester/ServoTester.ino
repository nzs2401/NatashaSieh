// Natasha Sieh
// Robotics 3
// 1/19/2023
// This program makes a micro servo manually controllable. When the button is pressed once, it goes to its half range position (1500). When the button is clicked a second time, it goes to sweep mode where it sweeps from the minimum to maximum range. When the button is clicked a third time, it goes back to the manually controlled mode.

#include <Servo.h>

Servo myservo;  // create servo object to control a servo


int potpin = 0;  // analog pin used to connect the potentiometer
int value;    // variable to read the value from the analog pin
int buttonState = 0;
int timesPressed = 0;
int angle = 0;
int buttonPin = 6;


void setup() {
Serial.begin(9600);
myservo.attach(9);  // attaches the servo on pin 9 to the servo object
pinMode(potpin, INPUT); // sets potpin as a input
pinMode(buttonPin, INPUT_PULLUP); // sets buttonPin as a input
}


void loop() {
  
  if (timesPressed == 0)
  {
    // MANUEL CODE
    //Serial.println(value);
    value = analogRead(potpin);            // reads the value of the potentiometer (value between 0 and 1023)
    value = map(value, 0, 1023, 900, 2160);    // scale it to use it with the servo (value between 0 and 180)
    myservo.writeMicroseconds(value);      // set servo to value
    Serial.println(value);
  }

  // button pressed
  buttonState = digitalRead(buttonPin);
  Serial.println("Button State");
  Serial.println(buttonState);

 // button is pressed
  if (buttonState == LOW)
  {
      // do loop to wait for buttonState to be high after pressed
      // if you keep the button pushed down and release it, it will move onto the next mode
      do
      {
        buttonState = digitalRead(buttonPin); // reads the button state
      } while(buttonState == LOW);
     
        // increment it by 1
        timesPressed++;
  }
        // if the button is pressed for the first time
       if (timesPressed == 1)
       {
           Serial.println("Button Pressed");
           // middle position
           myservo.writeMicroseconds(1500);
           Serial.println("Center");
           Serial.println(timesPressed);
           //delay(500);
       }

    // if the button is pressed for the second time
       else if (timesPressed == 2)
       {
           Serial.println("Sweep");
           Serial.println(timesPressed);

        // for loop that says that the servo will spin from 900 to 2160 and back with an increment of 50
               for (angle = 900; angle <= 2160; angle+=20)
               {    
                   myservo.writeMicroseconds(angle);    // prints out the angle of the servo after it runs through the for loop
                   delay(10);
                  
               }
          // for loop that says that the servo will spin from 2160 to 900 and back with an increment of 50
               for (angle = 2160; angle >= 900; angle-=20)
               {     // for loop that says that the servo will spin from 0 to 180 and back with an increment of 3
                   myservo.writeMicroseconds(angle);    // prints out the angle of the servo after it runs through the for loop
                   delay(10);
               }
        
       }
      // if the button is press for the third time
       else if (timesPressed == 3)
       {
           Serial.println("3 times!!!");
           timesPressed = 0;
           Serial.println(timesPressed);
       }
   
}
