#include <Arduino.h>
#include "ESP8266WiFi.h"  // Enables the ESP8266 to connect to the local network (via WiFi)
#include "PubSubClient.h" // Connect and publish to the MQTT broker



// define pins numbers
const int stepPin = 4; //D4 
const int dirPin = D2;  //D2
const int enablePin = D3;
const int top_cover_pin = D11;
const int bottom_cover_pin= D8;
const int window_pin = D12;

// MQTT settings
const char* mqtt_server = "192.168.0.108";  // IP of the MQTT broker = Raspberry
const char* window_topic = "home/livingroom/window/state"; // for rcv commands
const char* subscribe_topic = "home/livingroom/window/commands"; //for feedback that everything was correct
const char* mqtt_username = "jaberan"; // MQTT username
const char* mqtt_password = "temderku5j"; // MQTT password
const char* clientID = "client_window"; // MQTT client ID

const char* ssid = "Tenda_F1C9E0";                
const char* wifi_password = "wifi*31415926"; 

const bool up = true;
const bool down = false;
const bool opened = true;
const bool closed = false;

bool window_state = closed;

typedef enum {uncovered, not_defined, covered} cover_states;
volatile cover_states cover_state = not_defined;
volatile bool window_state_changed = false;

// Initialise the WiFi and MQTT Client objects
WiFiClient wifiClient;
PubSubClient client(mqtt_server, 1883, wifiClient); // 1883 is the listener port for the Broker

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

void move(bool dir, bool slow=false)
{
  enable_motor();
  int wait_time = slow ? 2: 1;
  if(dir == up)
  {
    digitalWrite(dirPin, LOW);
    while(cover_state != uncovered)
    {
      digitalWrite(stepPin,HIGH); 
      delay(wait_time);
      digitalWrite(stepPin,LOW); 
      delay(wait_time); 
    }
  }
  else //dir == down
  {
    digitalWrite(dirPin, HIGH);
    while(cover_state != covered)
    {
      digitalWrite(stepPin,HIGH); 
      delay(wait_time);
      digitalWrite(stepPin,LOW); 
      delay(wait_time); 
    }
  }
  disable_motor();
  /*
   * 
  digitalWrite(stepPin,HIGH); 
    delayMicroseconds(1000);
    digitalWrite(stepPin,LOW); 
    delayMicroseconds(1000); */
}

void callback(char* topic, byte* payload, unsigned int len)
{
  char msg[len+1];
  for(int i = 0; i < len; i++)
  {
    msg[i] = payload[i];
  }
  msg[len] = '\0';

  if(strcmp("up", msg) ==0)
  {
    move(up);
  }
  else if (strcmp("down", msg) ==0)
  {
    move(down);
  }
}

void ICACHE_RAM_ATTR int_cover_top_change()
{
  if(cover_state == not_defined)
  {
    cover_state = uncovered;
  }
  else if(cover_state == uncovered)
  {
    cover_state = not_defined;
  } 
}

void ICACHE_RAM_ATTR int_cover_bottom_change()
{
  if(cover_state == not_defined)
  {
    cover_state = covered;
  }
  else if(cover_state == covered) //pohyb zezdola nahoru
  {
    cover_state = not_defined;
  }  
}

void ICACHE_RAM_ATTR int_window_state_change()
{
 window_state_changed = true;  
}



void enable_motor()
{
  digitalWrite(enablePin, HIGH);
}

void disable_motor()
{
  digitalWrite(enablePin, LOW);
}



void get_endpoint()
{
 enable_motor();
 delay(1);
 //Pravděpodobně budou zaluzie vytazene - sjedu o otacku dolu
 digitalWrite(dirPin, HIGH); //TODO check jestli to jede spravne
 for(int i =0;i<400; i++)
  {
    digitalWrite(stepPin,HIGH); 
    delayMicroseconds(1000);
    digitalWrite(stepPin,LOW); 
    delayMicroseconds(1000); 
  }
  disable_motor();
  Serial.println("Pujdu vytahnout zaluzie...");
  move(up, true);
}



void cover()
{
  if(cover_state == covered)
    return;
  move(down);
}

void uncover()
{
  if(cover_state == uncovered)
    return;
  move(up);
}


void setup() {
  // Sets the two pins as Outputs

  pinMode(stepPin,OUTPUT); 
  pinMode(dirPin,OUTPUT);
  pinMode(D3, OUTPUT);
  
  Serial.begin(9600);
  cover_state = not_defined;

  WiFiConnect();
  MQTTConnect();
  client.setCallback(callback);
  client.subscribe(subscribe_topic); 
  Serial.println("OK2");
  pinMode(bottom_cover_pin, INPUT);
  pinMode(top_cover_pin, INPUT);
  pinMode(window_pin, INPUT);

  attachInterrupt(digitalPinToInterrupt(bottom_cover_pin), int_cover_bottom_change, CHANGE);
  attachInterrupt(digitalPinToInterrupt(top_cover_pin), int_cover_top_change, CHANGE);
  attachInterrupt(digitalPinToInterrupt(window_pin), int_window_state_change, CHANGE); 
  get_endpoint();
  


}


void loop() {
  client.loop(); //wait for subscribed topics

  if(window_state_changed)
  {
    
    if(window_state == closed)
      {
        window_state = opened;
        client.publish(window_topic, "open"); //
      }
    else
    {
      window_state = closed;
      client.publish(window_topic, "closed");
    }
    window_state_changed = false;
    Serial.print("Window state changed. Current state is: ");
    Serial.println(window_state ? "opened." : "closed.");
  }
}
