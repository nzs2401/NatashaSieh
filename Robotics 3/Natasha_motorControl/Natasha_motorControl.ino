// Natasha Sieh
// 5/21/23
// Robotics 3
// This is a program that uses a web server with ESP32 to:
// (1) change the speed and direction of brushless motor thru an ESC
// (2) uses a web slide to ramp up and back down the motor

#include <WiFi.h> 
#include <ESP32Servo.h>

#include<TFT_eSPI.h> //include TFT library
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI(); // Invoke library, pins defined in User_Setup.h


Servo myESC; // Make object of Servo motor from Servo library

// Objects are made for every servo motor,we want to control through this library

static const int ESC_GPIO = 13; // define the GPIO pin with which servo is connected

// Variables to store network name and password
const char* ssid = "R3-Natasha";
const char* password = "123456789";

// Set the server port nunber to deafualt 80
WiFiServer server(80);

// this variable header stores the HTTP requests data
String header;

//Zero Speed PWM (it´s not 1500, unfortunately)
int initialSpeed = 1470;  //change to the PWM that stops motor

// These variables used to store slider position 
String valueString = String(0);
int currentSpeed = initialSpeed;
int speedPercentage = 0;
String speed = String(currentSpeed);
int positon1 = 0;
int positon2 = 0;

void setup() 
{
	Serial.begin(115200); //define serial commuination with baud rate of 115200
  tft.begin();//initialize tft
  tft.setRotation(180);//set rotation to horizontal so text fits
  tft.fillScreen(TFT_BLACK); //fill the screen so it is black

	// Setup ESC Input
	myESC.attach(ESC_GPIO, 1000, 2000);


	Serial.print("Making connection to "); // it will display message on serial monitor
	Serial.println(ssid);

	WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();

	// These lines prints the IP address value on serial monitor 
	Serial.println("");
	Serial.println("WiFi connected.");
	Serial.println("IP address: ");
	Serial.println(IP);

	server.begin(); // It will start the servo motor with given position value. 

	// Start the BLDC motor at ZERO speed
	myESC.writeMicroseconds(currentSpeed);

}

void loop()
{
	WiFiClient client = server.available(); // Listen for incoming clients

	if (client)
	{ // If a new client connects,

		String header = client.readStringUntil('\r');
		client.println("HTTP/1.1 200 OK");
		client.println("Content-type:text/html");
		client.println("Connection: close");
		client.println();

		//For debugging purposes, display the header information
		Serial.print("Header:  ");
		Serial.println(header);

		// Display the HTML web page
		client.println("<!DOCTYPE html><html>");
		client.println("<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
		client.println("<link rel=\"icon\" href=\"data:,\">");
	
		// CSS to style the on/off buttons 
		// Feel free to change the background-color and font-size attributes to fit your preferences
		client.println("<style>body { text-align: center; font-family: \"Trebuchet MS\", Arial; margin-left:auto; margin-right:auto;}");
		client.println(".slider { width: 300px; }</style>");
		client.println("<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js\"></script>");

		// Web Page
		client.println("</head><body><h1>ESP32 with ESC</h1>");
		client.println("<p>Speed: <span id=\"servoPos\"></span>%</p>"); 
		client.println("<input type=\"range\" min=\"-100\" max=\"100\" class=\"slider\" id=\"servoSlider\" onchange=\"servo(this.value)\" value=\""+valueString+"\"/>");

		client.println("<script>var slider = document.getElementById(\"servoSlider\");");
		client.println("var servoP = document.getElementById(\"servoPos\"); servoP.innerHTML = slider.value;");
		client.println("slider.oninput = function() { slider.value = this.value; servoP.innerHTML = this.value; }");
		client.println("$.ajaxSetup({timeout:1000}); function servo(pos) { ");
		client.println("$.get(\"/?value=\" + pos + \"&\"); {Connection: close};}</script>");

		client.println("</body></html>"); 

		Serial.print("header.IndexOf: ");
		Serial.println(header.indexOf("GET /?value="));

		//GET /?value=180& HTTP/1.1
		if(header.indexOf("GET /?value=")>=0) 
		{
			positon1 = header.indexOf('=');
			positon2 = header.indexOf('&');
			valueString = header.substring(positon1+1, positon2);

      //String with New Speed Value
      valueString = header.substring(positon1+1, positon2);

      //Erase and Display new valueString
      tft.fillScreen(TFT_BLACK); //fill the screen so it is black

      tft.setTextColor(TFT_WHITE);
      tft.setTextSize(3); // Set text size to 1
      tft.setCursor(60, 160); // Set cursor position
      tft.println(valueString);

      //Convert Percentage Speed into PWM Value, adjust for initialSpeed being off
      speedPercentage = valueString.toInt();
      if (speedPercentage < 0) // this means it is CCW, so calculate the PWM for CCW
      {
        currentSpeed = (1000 + 400) + (4 * speedPercentage);
      }
      else if (speedPercentage > 0) // this means it is CW, so calculate the PWM for CW
      {
        currentSpeed = (initialSpeed + 30) + (5 * speedPercentage);
      }
      else
      {
        currentSpeed = initialSpeed; // speed is Zero
      }

			//Rotate the servo
			      myESC.writeMicroseconds(currentSpeed);

			Serial.println(valueString); 

      //Diaplay PWM speed on LCD
      tft.setTextColor(TFT_GREEN);
      tft.setTextSize(3); // Set text size to 1
      tft.setCursor(60, 280); // Set cursor position
      speed = String(currentSpeed);
      tft.println(speed);
		} 

		header = "";
		client.stop();
		Serial.println("Client disconnected.");
		Serial.println("");
	}
}
