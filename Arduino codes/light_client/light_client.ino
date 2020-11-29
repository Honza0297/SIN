#include <Arduino.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>
#include "ESP8266WiFi.h"  // Enables the ESP8266 to connect to the local network (via WiFi)
#include "PubSubClient.h" // Connect and publish to the MQTT broker
#include <RBDdimmer.h>//

#define outputPin  12 
#define zerocross  14 // for boards with CHANGEBLE input pins

/* 
 *  Address and command codes for RGB LED Livarno HG00197.
 *  The codes and address were reverse engineered by scanning
 *  IR commands from remote control using Arduino with IR receiver.
*/
uint16_t sAddress = 0x00; //puvodne 0xff00

const uint8_t commTurnOff = 0x1f;
const uint8_t commTurnOn = 0x0d;
const uint8_t commVolumeDown = 0x1d;
const uint8_t commVolumeUp = 0x09;
const uint8_t commWhite = 0x15;
const uint8_t commRed = 0x19;
const uint8_t commGreen = 0x1b;
const uint8_t commBlue = 0x11;
const uint8_t commOrange = 0x40;
const uint8_t commLightBlue = 0x12;
const uint8_t commViolet = 0x04;
const uint8_t commFade = 0x1a; //plynula zmena barvy 

/* Current state of the RGB*/
uint8_t currentState = commTurnOff;

// WiFi settings - hardcoded ssid and password. Zero security, 100 % simplicity. 
const char* ssid = "Tenda_F1C9E0";                
const char* wifi_password = "wifi*31415926"; 

// MQTT settings
const char* mqtt_server = "192.168.0.108";  // IP of the MQTT broker = Raspberry
const char* rgb_subscribe_topic = "home/livingroom/rgbled"; // for rcv commands
const char* rgb_publish_topic = "home/livingroom/rgbledfeedback"; //for feedback that everything was correct
const char* dim_subscribe_topic = "home/livingroom/dimmer";
const char* mqtt_username = "jaberan"; // MQTT username
const char* mqtt_password = "temderku5j"; // MQTT password
const char* clientID = "client_RGBLed"; // MQTT client ID


IRsend irsend(4);  //Object to send IR commands. 4 = D2 is the pin for IR LED
// Initialise the WiFi and MQTT Client objects
WiFiClient wifiClient;
PubSubClient client(mqtt_server, 1883, wifiClient); // 1883 is the listener port for the Broker
dimmerLamp dimmer(outputPin, zerocross); //initialase port for dimmer for ESP8266, ESP32, Arduino due boards

void callback_rgb(byte* payload, unsigned int len)
{
  // copy payload to char*
  char msg[len+1];
  for(int i = 0; i < len; i++)
  {
    msg[i] = payload[i];
  }
  msg[len] = '\0';
  /*10 bytes should be enough*/
  char * currentStateString = (char *)malloc(sizeof(char)*10);

  // Sens appropriate command
  if(strcmp("on", msg) == 0)
  {
    currentState = commTurnOn;
    currentStateString = "on"; 
  }
  else if(strcmp("off", msg) == 0)
  {
    currentState = commTurnOff;
    currentStateString = "off"; 
  }
  else if(strcmp("red", msg) == 0)
  {
    currentState = commRed;
    currentStateString = "red"; 
  }
  else if(strcmp("blue", msg) == 0)
  {
    currentState = commBlue;
    currentStateString = "blue"; 
  }
  else if(strcmp("green", msg) == 0)
  {
    currentState = commGreen;
    currentStateString = "green"; 
  }
  else if(strcmp("violet", msg) == 0)
  {
    currentState = commViolet;
    currentStateString = "violet"; 
  }
  else if(strcmp("orange", msg) == 0)
  {
    currentState = commOrange;
    currentStateString = "orange"; 
  }
  else if(strcmp("lightblue", msg) == 0)
  {
    currentState = commLightBlue;
    currentStateString = "lightblue"; 
  }
  else if(strcmp("up", msg) == 0)
  {
    currentState = commVolumeUp;
    currentStateString = "up"; 
  }
  else if(strcmp("down", msg) == 0)
  {
    currentState = commVolumeDown;
    currentStateString = "down"; 
  }
  else if(strcmp("white", msg) == 0)
  {
    currentState = commWhite;
    currentStateString = "white"; 
  }
  else if(strcmp("fade", msg) == 0)
  {
    currentState = commFade;
    currentStateString = "fade"; 
  }
  else
  {
    //pass
  }

  irsend.sendNEC(irsend.encodeNEC(sAddress,currentState));
  publishFeedback(currentStateString);
}

void callback_dimmer(byte *payload, unsigned int len)
{
  char msg[len+1];
  for(int i = 0; i < len; i++)
  {
    msg[i] = payload[i];
  }
  msg[len] = '\0';

  //thee will be int no matter what. 
  int power = atoi(msg);
  Serial.print("Dimmer request arrived. Value is: ");
  Serial.println(power);
  if(power < 0)
    dimmer.setPower(0);
  if(power > 100)
    dimmer.setPower(100);
    
  dimmer.setPower(power);
}


/**
 * Callback function which sends right commands to the RGB Led
*/
void callback(char* topic, byte* payload, unsigned int len)
{
  if(strcmp("home/livingroom/dimmer", topic) == 0)
    {
      callback_dimmer(payload, len);
    }
   else
   {
    callback_rgb(payload, len);
   }
}

/* Tries twice to send, then fails. */
void publishFeedback(char * feedback)
{
  for(int i = 0; i < 2; i++)
  {
    if (client.publish(rgb_publish_topic, feedback)) 
    {
    Serial.print("Feedback sent with value ");
    Serial.println(feedback);
    return;
    }
    else {
      Serial.println("Feedback failed to send. Reconnecting to MQTT Broker and trying again");
      MQTTConnect();
      delay(10); // This delay ensures that client.publish doesn't clash with the client.connect call
    }
  }
  free(feedback);
}

void WiFiConnect()
{
  Serial.print("Connecting to ");
  Serial.println(ssid);

  // Connect to the WiFi
  WiFi.begin(ssid, wifi_password);

  // Wait until the connection has been confirmed before continuing
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("The state is:");
    Serial.println(WiFi.status());
    }

  // Debugging - Output the IP Address of the ESP8266
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// Custom function to connet to the MQTT broker via WiFi
void MQTTConnect(){
  // Connect to MQTT Broker
  // client.connect returns a boolean value to let us know if the connection was successful.
  // If the connection is failing, make sure you are using the correct MQTT Username and Password (Setup Earlier in the Instructable)
  if (client.connect(clientID, mqtt_username, mqtt_password)) {
    Serial.println("Connected to MQTT Broker!");
  }
  else {
    Serial.println("Connection to MQTT Broker failed...");
  }
}

void setup() {
  irsend.begin();
  Serial.begin(9600);
  WiFiConnect();
  MQTTConnect();

  /*set what function will handle subscribed topics and what topics I want to subscribe to.*/
  client.setCallback(callback);
  client.subscribe(rgb_subscribe_topic);
  client.subscribe(dim_subscribe_topic);
  dimmer.begin(NORMAL_MODE, ON); //dimmer initialisation: name.begin(MODE, STATE) 
}

void loop() {
  /* Subscribe */
  client.loop(); //wait for subscribed topics
  delay(100); // delay to save power
}
