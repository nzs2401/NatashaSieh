#include <TFT_eSPI.h>


TFT_eSPI tft;


void setup() {
  tft.begin();
  tft.setRotation(3); // Rotate display 270 degrees
  tft.fillScreen(TFT_BLACK); // Set background color to black
}


void loop() {
  tft.setTextColor(TFT_WHITE, TFT_BLACK); // Set text color to white, background to black
  tft.setTextSize(3); // Set text size to 3
  tft.setCursor(20, 50); // Set cursor position
  tft.println("Your Name");


  tft.setTextSize(2); // Set text size to 2
  tft.setCursor(20, 120); // Set cursor position
  tft.println("I'm sorry, Dave.");
  tft.setCursor(20, 150); // Set cursor position
  tft.println("I'm afraid I can't do that.");


  delay(3000); // Wait for 3 seconds


  tft.fillScreen(TFT_BLACK); // Clear screen


  tft.drawRect(30, 30, 80, 80, TFT_RED); // Draw rectangle
  tft.drawCircle(150, 100, 40, TFT_GREEN); // Draw circle
  tft.drawSquare(30, 130, 80, TFT_BLUE); // Draw square
  tft.drawLine(150, 150, 200, 100, TFT_YELLOW); // Draw line


  delay(3000); // Wait for 3 seconds


  tft.fillScreen(TFT_BLACK); // Clear screen
}
