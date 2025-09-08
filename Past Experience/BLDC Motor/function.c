// Natasha Sieh
// 4/14/23
// Robotics 3
// This is a program that uses a rotary encoder to:
//    (1) change the speed and direction of brushless motor thru an ESC
//    (2) used the rotary encoder button to ramp up and back down the motor  
 
//Libraries needed for the rotary encoder and the ESC functions
#include <Encoder.h>
#include <Servo.h>
 
// Rotary Encoder Inputs
#define CLK 2
#define DT 3
#define SW 4
 
// ESC Input
#define ESC_PIN  9
 
// Create servo object to control the ESC
Servo myESC;
 
// Variables to be used with the rotary encoder
int counter = 0;  //start the counter at zero, which is ZERO speed
int rotaryChange = 0; //tells if rotary has changed position, 1 is yes, 0 is no
int currentStateCLK;  //holds the current state of CLK input
int lastStateCLK;     // holds the last state of CLK input​
String currentDir =""; //holds the last direction change of the rotary encoder
 
int buttonPressed = 0;  // tells if button was pressed, 1 is yes, 0 is no
int buttonInterval = 1000;  //how long button needs to be pressed to activate in ms
int lastStateSW = LOW;  // the previous state from the button
int currentStateSW;     // the current reading from the button
unsigned long pressedTime  = 0; //holds the time button was pressed
unsigned long releasedTime = 0; //holds the time button was released
long pressDuration = 0;  //holds the time duration the button was pressed
// Variables holding ESC PWM Configuration
int max_CW_Speed = 2000;  // corresponds to ESC Max Clockwise speed in PWM
int max_CCW_Speed = 1000;  // corresponds to ESC Max Counter-Clockwise speed in PWM
int initialSpeed = 1500;  // initial ZERO speed in PWM
 
// Variables to manage the speed changes
int speedChange = 50;   // PWN equal to 10% change in speed
int newSpeed = initialSpeed;  //holds the new speed to write to the ESC
 
int waitInterval = 500; //amount in milliseconds to wait between speed changes
unsigned long startMillis; // holds the initial timestamp
unsigned long currentMillis; // holds the current timestamp
 
void setup()
{
    // Set encoder pins as inputs
    pinMode(CLK,INPUT);
    pinMode(DT,INPUT);
    pinMode(SW, INPUT_PULLUP);
    
    // Setup Serial Monitor
    Serial.begin(9600);
    
    Serial.println("Initializing");
    
    // Setup ESC Input
    myESC.attach(ESC_PIN, max_CCW_Speed, max_CW_Speed);
    
    // Start the BLDC motor at ZERO speed
    myESC.writeMicroseconds(initialSpeed);

    // Read the initial state of CLK
    lastStateCLK = digitalRead(CLK);
 
}
 

void loop()
{
    // Read the rotary encoder for rotation change
        rotaryChange = rotaryRead();
    
    // Only change speed if rotary encoder was rotated
    if (rotaryChange != 0)
    {
    //increase or decrease counter based on rotation of encoder
        counter = counter + rotaryChange;
        
        // if counter is more than 10 or less than -10,
        // then reset it to 10 or-10 respectively, since it is at max speeds
        if (counter < -10) 
        {
             counter = -10;
        }
        if (counter > 10) 
        {
             counter = 10;
        }
        
        // Calculate new speed based on counter value
        newSpeed = initialSpeed + (counter * speedChange);
        
        // Send new speed to ESC
        myESC.writeMicroseconds(newSpeed);
    
        // Display changes to Serial Monitor
        Serial.print("Direction: ");
        Serial.print(currentDir);
        Serial.print(" | Counter: ");
        Serial.print(counter);
        Serial.print(" | Speed: ");
        Serial.println(newSpeed);
    
    }
    
    // Read the button state only if counter is 0 (motor at ZERO speed)
    if (counter == 0)
    {
        //Find out if the button was pressed for required time
        buttonPressed = buttonRead();
        
        // if button was pressed then execute automatic
        // speed up and speed down
        if (buttonPressed == 1)
        {
            // Start the speed up process
            Serial.println("Accelerating");
            
            // Accelerate motor by speedChange intervals,  
            // starting at initialSpeed and up to max_CW_Speed
            for (int i = initialSpeed + speedChange; i <= max_CW_Speed; i = i + speedChange)
            {
                //Display speed changes as it ramps up
                Serial.print("Speed: ");
                Serial.println(i);
                
                // Up motor speed via new PWM
                myESC.writeMicroseconds(i);
                
                // Wait an Interval before each increment
                currentMillis = millis();
                startMillis = currentMillis;
                do {
                   currentMillis = millis();
                } while (currentMillis - startMillis <= waitInterval);
            }
            
            // Start the speed down process
            Serial.println("De-accelerating");
            
            // Now de-accelerate motor by speedChange,
            // starting at max_CW_Speed back to initialSpeed
            
            for (int y = max_CW_Speed - speedChange; y >= initialSpeed; y = y - speedChange)
            {
                //Display speed changes as it ramps down
                Serial.print("Speed: ");
                Serial.println(y);
                
                // Down motor speed via new PWM
                myESC.writeMicroseconds(y);
                
                // Wait an Interval before each decrement
                currentMillis = millis();
                startMillis = currentMillis;
                do {
                   currentMillis = millis();
                } while (currentMillis - startMillis <= waitInterval);
            }
            // Display completion of Automatic Speed Routine
            Serial.println("Auto Speed Completed.");
        }
    }
}
 


// rotaryRead - Function to read rotary encoder
// Returns 1 if rotated CW, -1 if rotated CCW, and 0 otherwise.
int rotaryRead()
{
    // Read the current state of CLK
    currentStateCLK = digitalRead(CLK);
    
    // If last and current state of CLK are different,
    // then pulse occurred
    // React to only 1 state change to avoid double count
    if (currentStateCLK != lastStateCLK  && currentStateCLK == 1)
    {
        // If the DT state is different than the CLK state then
        // the encoder is rotating CCW so decrement
        if (digitalRead(DT) != currentStateCLK) 
        {
            currentDir ="CCW";
            // Remember last CLK state
            lastStateCLK = currentStateCLK;
            return -1;
        }
        else
        {
            // Encoder is rotating CW so increment
            currentDir ="CW";
            // Remember last CLK state
            lastStateCLK = currentStateCLK;
            return 1;
        }
    }
    // Remember last CLK state
    lastStateCLK = currentStateCLK;
    return 0;
}
 

// buttonRead – Function to find out if button has been pressed for the required
//  time.  Returns 1, if pressed.  Otherwise, returns 0
 
int buttonRead()
{
    // Read the SW input
    currentStateSW = digitalRead(SW);
    
    if(lastStateSW == HIGH && currentStateSW == LOW)
    {
        // Button is pressed, record the time
        pressedTime = millis();
    }
    else if(lastStateSW == LOW && currentStateSW == HIGH)
    {
        // Button is released, record the time
         releasedTime = millis();
        
        // Calculate how long the button was pressed and then released
        pressDuration = releasedTime - pressedTime;
        
        // Only considered pressed if button was held down & released
        // for minimum specified Interval
        if( pressDuration > buttonInterval )
        {
            Serial.println("Button Pressed detected!");
        
            // save the last state
            lastStateSW = currentStateSW;
            return 1;  // Button considered pressed
        }
    }
    // save the last state 
    lastStateSW = currentStateSW;
    return 0;  // Button not considered pressed
}
