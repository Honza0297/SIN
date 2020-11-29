import paho.mqtt.client as paho


# broker="192.168.0.108"
# port=1883

# Callback function for MQTT
def on_publish(client, userdata, result):
    print("data published")


class LEDPublisher:
    """
    Publisher controlling both room and RGB LED bulbs.
    """
    def __init__(self):
        self.broker = "192.168.0.108"
        self.port = 1883

        self.client = paho.Client("LEDController")
        self.client.username_pw_set("jaberan", "temderku5j")

        self.client.on_publish = on_publish  # assign function to callback
        self.client.connect(self.broker, self.port)  # establish connection

    def reconnect(self):
        self.client.reconnect()  # establish connection

    # This methos controlls RGB bulb. Example commands are "on", "red", "fade"
    def rgb_command(self, command):
        self.reconnect()
        self.client.publish("home/livingroom/rgbled", command)

    # This method controls light bulb in a little "simplified" mode. It sends value from 0 to 100 which
    # corresponds to percentage of light intensity. However, under 30 (%), the light is almost invisible
    # -> it it not linear scale.
    def dimmer_command(self, val):
        self.reconnect()
        self.client.publish("home/livingroom/dimmer", val)
