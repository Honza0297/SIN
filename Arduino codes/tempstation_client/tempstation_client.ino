#include <Arduino.h>
#include "ESP8266WiFi.h"  // Enables the ESP8266 to connect to the local network (via WiFi)
#include "PubSubClient.h" // Connect and publish to the MQTT broker.h"  // Enables the ESP8266 to connect to the local network (via WiFi)

#include "DHT.h"

#define DHTPIN 2
#define GASENABLEPIN 5
// řekneme, že senzor je typu DHT-22 
#define DHTTYPE DHT11 


// WiFi settings - hardcoded ssid and password. Zero security, 100 % simplicity. 
const char* ssid = "Tenda_F1C9E0";                
const char* wifi_password = "12345678"; //Such strong!


// MQTT settings
const char* mqtt_server = "192.168.0.105";  // IP of the MQTT broker = Raspberry
const char* temp_publish_topic = "home/livingroom/temp"; // for rcv commands
const char* hum_publish_topic = "home/livingroom/hum"; //for feedback that everything was correct
const char* gas_publish_topic = "home/livingroom/gas";
const char* request_subscribe_topic = "home/livingroom/tempstation";

const char* mqtt_username = "jaberan"; // MQTT username
const char* mqtt_password = "temderku5j"; // MQTT password
const char* clientID = "client_tempstation"; // MQTT client ID

DHT dht(DHTPIN, DHTTYPE);
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

int get_gas_value()
{
  digitalWrite(GASENABLEPIN, HIGH);
  delay(5000); //preheat to get at least +- accurate values
  int val = analogRead(A0);
  Serial.println(val);
  digitalWrite(GASENABLEPIN, LOW);
  return val; //avg = 2500 (max 3000), problem  is > 3500
}

void callback(char* topic, byte* payload, unsigned int len)
{
  char msg[len+1];
  for(int i = 0; i < len; i++)
  {
    msg[i] = payload[i];
  }
  msg[len] = '\0';
  char *feedback = (char*)malloc(sizeof(char)*5); //max value from humidity and temp is 100 
  const char * publish_topic;
  int value=0;
  if(strcmp("gas", msg) == 0)
  {
    value =  get_gas_value();
    publish_topic = gas_publish_topic;
  } 
  else if (strcmp("temp", msg) == 0)
  {
    value = dht.readTemperature();
    publish_topic = temp_publish_topic;
  }
  else if(strcmp("humidity", msg)== 0)
  {
    value = dht.readHumidity();
    publish_topic = hum_publish_topic;
  }
  else
  {
    //pass
  }
  sprintf(feedback, "%d", value); //int to string
  publishFeedback(feedback, (char *)publish_topic);
}

void publishFeedback(char * feedback, char *topic)
{
  for(int i = 0; i < 2; i++)
  {
    if (client.publish(topic, feedback)) 
    {
    Serial.print("Feedback sent with value ");
    Serial.println(feedback);
    free(feedback);
    return;
    }
    else {
      Serial.println("Feedback failed to send. Reconnecting to MQTT Broker and trying again");
      MQTTConnect();
      delay(10); // This delay ensures that client.publish doesn't clash with the client.connect call
    }
  }
  
}



 

void setup() {
  dht.begin();
  Serial.begin(9600);   
  pinMode(DHTPIN, INPUT_PULLUP);
  pinMode(GASENABLEPIN,OUTPUT); //gas enable
  pinMode(A0,INPUT); //gas value
  
  WiFiConnect();
  MQTTConnect();
  
  client.setCallback(callback);
  client.subscribe(request_subscribe_topic);
                      
                                  
}



void loop() {
  /*// put your main code here, to run repeatedly:
  Serial.print("Vlhkost: ");                
  Serial.print(dht.readHumidity());
  Serial.print(" %, Teplota: ");
  Serial.print(dht.readTemperature());
  Serial.println(" Celsius");
  Serial.println(get_gas_value());
  /*digitalWrite(22, LOW);
  delay(1000);
  digitalWrite(22, HIGH);*/
  // počkáme 2s před opakováním měření
  client.loop(); //wait for subscribed topics
  delay(100); // delay to save power             
}
