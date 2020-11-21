import paho.mqtt.client as paho
import time


# broker="192.168.0.105"
# port=1883

class TempstationPublisher:
    def __init__(self):
        self.temp = 0
        self.broker = "192.168.0.105"
        self.port = 1883
        self.topic = "home/livingroom/tempstation"

        self.client = paho.Client("TempstationController")
        self.client.username_pw_set("jaberan", "temderku5j")

        self.client.on_publish = self.on_publish
        self.client.connect(self.broker, self.port)  # establish connection
        self.client.subscribe("home/livingroom/temp")
        self.client.subscribe("home/livingroom/hum")
        self.client.subscribe("home/livingroom/gas")

    def on_publish(self, client, userdata, result):  # create function for callback
        print("data published")

    def request_temperature(self):
        self.client.reconnect()
        self.client.publish(self.topic, "temp")

    def request_humidity(self):
        self.client.reconnect()
        self.client.publish(self.topic, "humidity")

    def request_gas(self):
        self.client.reconnect()
        self.client.publish(self.topic, "gas")

class TempstationSubscriber:
    def __init__(self):
        self.temp = 0
        self.hum = 0
        self.gas = 0

        self.broker = "192.168.0.105"
        self.port = 1883

        self.client = paho.Client("TempstationSubscriber")
        self.client.username_pw_set("jaberan", "temderku5j")

        self.client.connect(self.broker, self.port)  # establish connection

    def reconnect(self):
        self.client.reconnect()
        self.client.on_message = self.on_message
        self.client.subscribe("home/livingroom/temp")
        self.client.subscribe("home/livingroom/hum")
        self.client.subscribe("home/livingroom/gas")

    def on_message(self, client, userdata, message):  # create function for callback
        if message.topic == "home/livingroom/temp":
            self.process_temp(message)
        elif message.topic == "home/livingroom/hum":
            self.process_hum(message)
        elif message.topic == "home/livingroom/gas":
            self.process_gas(message)

    def process_temp(self, message):
        # TODO ulozit do db
        # TODO pripadne pingnout RulerMastera
        print("Temperature is:" + str(message.payload))

    def process_hum(self, message):
        # TODO ulozit do db
        # TODO pripadne pingnout RulerMastera
        print("Humidity is:" + str(message.payload))

    def process_gas(self, message):
        # TODO ulozit do db
        # TODO pripadne pingnout RulerMastera
        print("Gas value is:" + str(message.payload))

    def run(self):
        self.reconnect()
        self.client.loop_forever()
