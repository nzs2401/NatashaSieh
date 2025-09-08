#include <Servo.h>

Servo servo1;
Servo servo2;

void setup() {
  // put your setup code here, to run once:
  servo1.attach( 2 ); //digital pin or colored wire
  servo2.attach( 3 ); //digital pin or colored wire

}

int deg = 90; // starting position
int incr = 1; // how much to move in each cycle
void loop() {
  // put your main code here
  deg += incr; // deg = deg + incr 
  if( deg < 5 )
    incr = 1;
  if ( deg > 175 )
    incr = -1;
   servo1.write( deg );
   servo2.write( deg );
   delay( 3000/170 ); 
}
