import paho.mqtt.client as paho


def receive(client, userdata, message):
    print(client, userdata, message.payload)


class Subscriber_all:
    """
    This class is used to subscribe to all MQTT messages. Mostly for testing.
    """
    def __init__(self):
        broker = "192.168.0.108"
        port = 1883
        self.client = paho.Client("subscriber_all_topics")
        self.client.username_pw_set("jaberan", "temderku5j")
        self.client.connect(broker, port)

    def start_subscribing(self):
        self.client.on_message = receive
        self.client.subscribe("home/#")  # subscribe to all messages
        self.client.loop_forever()
