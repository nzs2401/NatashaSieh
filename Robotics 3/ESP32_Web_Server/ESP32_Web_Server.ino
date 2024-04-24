/*********
Natasha Sieh
Complete project details at https://randomnerdtutorials.com  
*********/

// Load Wi-Fi library
#include <WiFi.h>
#include<TFT_eSPI.h>//include TFT library
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h


// Replace with your network credentials
const char* ssid     = "R3-Natasha";
const char* password = "123456789";

// Set web server port number to 80
WiFiServer server(80);

// Variable to store the HTTP request
String header;

// Auxiliar variables to store the current output state
String output12State = "off";
String output13State = "off";

// Assign output variables to GPIO pins
const int output12 = 12;
const int output13 = 13;

void setup() {
  Serial.begin(115200);//begin serial and set baud
   tft.begin();//initialize tft
   tft.setRotation(180);//set rotation to horizontal so text fits
   tft.fillScreen(TFT_BLACK); //fill the screen so it is black
  Serial.begin(115200);
  // Initialize the output variables as outputs
  pinMode(output12, OUTPUT);
  pinMode(output13, OUTPUT);
  // Set outputs to LOW
  digitalWrite(output12, LOW);
  digitalWrite(output13, LOW);

  // Connect to Wi-Fi network with SSID and password
  Serial.print("Setting AP (Access Point)…");
  // Remove the password parameter, if you want the AP (Access Point) to be open
  WiFi.softAP(ssid, password);

  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);
  
  server.begin();

  tft.setTextSize(1); // Set text size to 1
  tft.setCursor(0, 0); // Set cursor position
  tft.println("SSID: ESP32-natasha");
  tft.setCursor(0, 5); // Set cursor position
  tft.println("PWD: 123456789");
  tft.setCursor(0, 10); // Set cursor position
  tft.println("IP: 192.168.4.1");
  

  //tft.drawCircle(85, 230, 35, TFT_GREEN); // Draw green circle
  //tft.drawCircle(85, 110, 35, TFT_BLUE); // Draw red circle
}

void loop(){
  tft.drawCircle(85, 230, 35, TFT_GREEN); // Draw green circle
  tft.drawCircle(85, 110, 35, TFT_BLUE); // Draw red circle

  WiFiClient client = server.available();   // Listen for incoming clients

  if (client) {                             // If a new client connects,
    Serial.println("New Client.");          // print a message out in the serial port
    String currentLine = "";                // make a String to hold incoming data from the client
    while (client.connected()) {            // loop while the client's connected
      if (client.available()) {             // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        Serial.write(c);                    // print it out the serial monitor
        header += c;
        if (c == '\n') {                    // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();
            
            // turns the GPIOs on and off
            if (header.indexOf("GET /26/on") >= 0) {
              Serial.println("GPIO 26 on");
              output12State = "on";
              digitalWrite(output12, HIGH);
            } else if (header.indexOf("GET /26/off") >= 0) {
              Serial.println("GPIO 26 off");
              output12State = "off";
              digitalWrite(output12, LOW);
            } else if (header.indexOf("GET /27/on") >= 0) {
              Serial.println("GPIO 27 on");
              output13State = "on";
              digitalWrite(output13, HIGH);
            } else if (header.indexOf("GET /27/off") >= 0) {
              Serial.println("GPIO 27 off");
              output13State = "off";
              digitalWrite(output13, LOW);
            }
            
            // Display the HTML web page
            client.println("<!DOCTYPE html><html>");
            client.println("<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
            client.println("<link rel=\"icon\" href=\"data:,\">");
            // CSS to style the on/off buttons 
            // Feel free to change the background-color and font-size attributes to fit your preferences
            client.println("<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}");
            client.println(".button { background-color: #4CAF50; border: none; color: white; padding: 16px 40px;");
            client.println("text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}");
            client.println(".button2 {background-color: #555555;}</style></head>");
            
            // Web Page Heading
            client.println("<body><h1>ESP32 Web Server</h1>");
            
            // Display current state, and ON/OFF buttons for GPIO 26  
            client.println("<p>GPIO 26 - State " + output12State + "</p>");
            // If the output12State is off, it displays the ON button       
            if (output12State=="off") {
              client.println("<p><a href=\"/26/on\"><button class=\"button\">ON</button></a></p>");
              tft.drawCircle(85, 110, 35, TFT_BLUE); // Draw outline of green circle
              tft.setTextColor(TFT_BLUE);
              tft.setTextSize(3); // Set text size to 1
              tft.setCursor(60, 160); // Set cursor position
              tft.println("OFF");
              
            } else {
              client.println("<p><a href=\"/26/off\"><button class=\"button button2\">OFF</button></a></p>");
              tft.fillCircle(85, 110, 35, TFT_BLUE); // Draw outline of green circle
              tft.drawCircle(85, 110, 35, TFT_BLUE); // Draw outline of green circle
              tft.setTextSize(3); // Set text size to 1
              tft.setCursor(60, 160); // Set cursor position
              tft.println("ON");
            } 
               
            // Display current state, and ON/OFF buttons for GPIO 27  
            client.println("<p>GPIO 27 - State " + output13State + "</p>");
            // If the output13State is off, it displays the ON button       
            if (output13State=="off") {
              client.println("<p><a href=\"/27/on\"><button class=\"button\">ON</button></a></p>");
              tft.drawCircle(85, 230, 35, TFT_GREEN); // Draw outline of green circle
              tft.setTextColor(TFT_GREEN);
              tft.setTextSize(3); // Set text size to 1
              tft.setCursor(60, 280); // Set cursor position
              tft.println("OFF");
            } else {
              client.println("<p><a href=\"/27/off\"><button class=\"button button2\">OFF</button></a></p>");
              tft.fillCircle(85, 230, 35, TFT_GREEN); // fill green circle
            }
            client.println("</body></html>");
            
            // The HTTP response ends with another blank line
            client.println();
            // Break out of the while loop
            break;
          } else { // if you got a newline, then clear currentLine
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
    // Clear the header variable
    header = "";
    // Close the connection
    client.stop();
    Serial.println("Client disconnected.");
    Serial.println("");
  }
}
