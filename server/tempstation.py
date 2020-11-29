import paho.mqtt.client as paho
import time
import InfluxBridge
import sys
# broker="192.168.0.108"
# port=1883


class TempstationPublisher:
    """
    Class publishes requests via MQTT to the temperature station.
    """
    def __init__(self):
        self.broker = "192.168.0.108"
        self.port = 1883
        self.topic = "home/livingroom/tempstation"

        self.client = paho.Client("TempstationController")
        self.client.username_pw_set("jaberan", "temderku5j")

        self.client.on_publish = self.on_publish
        self.client.connect(self.broker, self.port)  # establish connection
        self.client.subscribe("home/livingroom/temp")
        self.client.subscribe("home/livingroom/hum")
        self.client.subscribe("home/livingroom/gas")

    # Callback function for mqtt
    def on_publish(self, client, userdata, result):
        sys.stderr.write("data published")

    def request_temperature(self):
        self.client.reconnect()
        self.client.publish(self.topic, "temp")

    def request_humidity(self):
        self.client.reconnect()
        self.client.publish(self.topic, "humidity")

    def request_gas(self):
        self.client.reconnect()
        self.client.publish(self.topic, "gas")

    def continuous_publishing(self, period=600):
        while True:
            self.request_temperature()
            self.request_humidity()
            time.sleep(period)


class TempstationSubscriber:
    """
    Subscribes to MQTT temperature station.
    """
    def __init__(self):
        self.temp = 0
        self.hum = 0
        self.gas = 0
        self.bridge = InfluxBridge.InfluxBridge()
        self.broker = "192.168.0.108"
        self.port = 1883

        self.client = paho.Client("TempstationSubscriber")
        self.client.username_pw_set("jaberan", "temderku5j")

        self.client.connect(self.broker, self.port)  # establish connection

    # MQTT client can disconnect after timeout - this automatically reconnects him and make him subscribe to appropriate topics
    def reconnect(self):
        self.client.reconnect()
        self.client.on_message = self.on_message
        self.client.subscribe("home/livingroom/temp")
        self.client.subscribe("home/livingroom/hum")
        self.client.subscribe("home/livingroom/gas")

    # MQTT incoming message handler
    def on_message(self, client, userdata, message):
        if message.topic == "home/livingroom/temp":
            self.process_temp(message)
        elif message.topic == "home/livingroom/hum":
            self.process_hum(message)
        elif message.topic == "home/livingroom/gas":
            self.process_gas(message)

    def process_temp(self, message):
        self.bridge.store_data("temperature", message.payload.decode("utf-8"))
        # TODO pripadne pingnout RulerMastera
        sys.stderr.write("Temperature is:" + message.payload.decode("utf-8"))

    def process_hum(self, message):
        self.bridge.store_data("humidity", message.payload.decode("utf-8"))
        # TODO pripadne pingnout RulerMastera
        sys.stderr.write("Humidity is:" + message.payload.decode("utf-8"))

    def process_gas(self, message):
        self.bridge.store_data("gas", message.payload.decode("utf-8"))
        # TODO pripadne pingnout RulerMastera
        sys.stderr.write("Gas value is:" + message.payload.decode("utf-8"))

    def run(self):
        self.reconnect()
        self.client.loop_forever()
