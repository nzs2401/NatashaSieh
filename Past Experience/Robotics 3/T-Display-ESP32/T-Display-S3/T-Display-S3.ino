//read temp and prints to a monitor


#include<OneWire.h>//include one wire library
#include<DallasTemperature.h>//include dallas temperature library
#include<TFT_eSPI.h>//include tft library
#include<SPI.h>//include spi stuff


int oneWireBus = 1;// CONNECT IT TO one PLS
OneWire oneWire(oneWireBus);//Setup a oneWire instance to communicate with any OneWire devices
DallasTemperature sensors(&oneWire);//Pass our oneWire reference to Dallas Temperature sensor
TFT_eSPI tft = TFT_eSPI();//making TFT_eSPI tft equal to the TFT_eSPI function


void setup() {
  // put your setup code here, to run once:
   Serial.begin(115200);//begin serial and set baud
   sensors.begin();//start sensors
   tft.init();//initialize tft
   tft.setRotation(1);//set rotation to horizontal so text fits
   tft.fillScreen(TFT_BLACK);//fill the screen so it is black
}


void loop() {
  // put your main code here, to run repeatedly:
  sensors.requestTemperatures(); //get the temps from sensors
   float temperatureC = sensors.getTempCByIndex(0);//store temps in celsius as a float
   float temperatureF = sensors.getTempFByIndex(0);//store temps in farenheight as a float
  tft.drawString(String(temperatureC),10,10,2);//print the temp in celsius
  tft.drawString("degrees celsius",60,10,2);//print label for temp in c
  tft.drawString(String(temperatureF),10,30,2);//print the temp in farenheight
  tft.drawString("degrees farenheight",60,30,2);//print label for temp in f
}
