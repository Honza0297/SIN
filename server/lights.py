import paho.mqtt.client as paho


# broker="192.168.0.105"
# port=1883

def on_publish(client, userdata, result):  # create function for callback
    print("data published")


class LEDPublisher:
    def __init__(self):
        self.broker = "192.168.0.105"
        self.port = 1883

        self.client = paho.Client("LEDController")
        self.client.username_pw_set("jaberan", "temderku5j")

        self.client.on_publish = on_publish  # assign function to callback
        self.client.connect(self.broker, self.port)  # establish connection

    def reconnect(self):
        self.client.reconnect()  # establish connection

    def rgb_command(self, command):
        self.reconnect()
        self.client.publish("home/livingroom/rgbled", command)  # publish

    def dimmer_command(self, val):
        self.reconnect()
        self.client.publish("home/livingroom/dimmer", val)
