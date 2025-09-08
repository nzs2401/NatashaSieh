/*  
 Test the tft.print() viz embedded tft.write() function

 This sketch used font 2, 4, 7
 
 Make sure all the display driver and pin connections are correct by
 editing the User_Setup.h file in the TFT_eSPI library folder.

 Note that yield() or delay(0) must be called in long duration for/while
 loops to stop the ESP8266 watchdog triggering.

 #########################################################################
 ###### DON'T FORGET TO UPDATE THE User_Setup.h FILE IN THE LIBRARY ######
 #########################################################################
 */


#include <TFT_eSPI.h> // Graphics and font library for ST7735 driver chip
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h

#define TFT_GREY 0x5AEB // New colour

void setup() {
  tft.begin();
  tft.setRotation(3); // Rotate display 270 degrees
  tft.fillScreen(TFT_BLACK); // Set background color to black
}


void loop() {
  tft.setTextColor(TFT_WHITE, TFT_BLACK); // Set text color to white, background to black
  tft.setTextSize(3); // Set text size to 3
  tft.setCursor(20, 50); // Set cursor position
  tft.println("Natasha");


  tft.setTextSize(1); // Set text size to 2
  tft.setCursor(20, 120); // Set cursor position
  tft.println("I'm sorry, Dave. I'm afraid I can't do that.");
  //tft.setCursor(15, 150); // Set cursor position
  //tft.println("I'm afraid I can't do that.");


  delay(3000); // Wait for 3 seconds


  tft.fillScreen(TFT_BLACK); // Clear screen


  tft.drawRect(30, 30, 80, 80, TFT_RED); // Draw rectangle
  tft.fillCircle(150, 100, 40, TFT_YELLOW); // Draw circle
  tft.drawCircle(30, 130, 80, TFT_BLUE); // Draw square
  tft.drawLine(150, 150, 200, 100, TFT_YELLOW); // Draw line
  tft.drawTriangle(43, 30, 40, 90, 80, 120, TFT_PINK);

  delay(3000); // Wait for 3 seconds


  tft.fillScreen(TFT_BLACK); // Clear screen
}
