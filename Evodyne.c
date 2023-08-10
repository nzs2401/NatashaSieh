#include "ServoDriver.h"

ServoDriver servo_driver;

void servogoto(char servo_id, int pos)
{ // degrees
  servo_driver.gotoPos(servo_id, pos+90);
}

// calculating the degrees
double getanglebc(double ab, double bc, double ca)
{
  double v = (ab*ab + bc*bc - ca*ca) / (2.0 * ab * bc);
  if (v > 1)
    v = 1;
  if (v < -1)
    v = -1;
  return (acos(v) * RAD_TO_DEG);
//        ^^^ arc cosine  ^^^^^ Radians to Degrees
}

#define LTHIGH 100.0 // hip to knee
#define LCALF 125.327 // foot to hip

// for ONE leg only:
 class Leg
 {
  public:
  void gotoAng(float hip, float knee)
  {
    servogoto(0, hip);
    servogoto(1, knee-45);
  }

  void calcAngles( float x, float y, float& h, float& k ) //from xy position
  {
    double max_length = LTHIGH + LCALF;
    double l = sqrt(x * x + y * y); //length of leg in desired  position
    if ( l > max_length )
      l = max_length;
    double l_hip = getanglebc( LTHIGH, l, LCALF);
    double l_angle = getanglebc( l, y, x );
    if ( x < 0 )
      l_angle = -l_angle;
    double hip_angle = l_hip + l_angle;

    double knee_angle = 180.0 - getanglebc( LCALF, LTHIGH, l );
    h = hip_angle;
    k = knee_angle;
   }
   void gotoXY(float x, float y)
   {
    float hip;
    float knee;
    calcAngles(x,y,hip,knee);
    gotoAng(hip,knee);
   }
   
 };
Leg leg;

void setup() {
  // put your setup code here, to run once:
  servo_driver.setup();
}

void loop() {
  // put your main code here, to run repeatedly:
  /* for (int x = -30; x < 30; x++)
  {
    leg.gotoXY(x,180);
    delay(30);
  }
    for (int x = 30; x > -30; x--)
  {
    leg.gotoXY(x,180);
    delay(30);
  } */
  leg.gotoAng(0,0);
  delay(3000);
  
  leg.gotoAng(30,30);
  delay(3000);      
}
