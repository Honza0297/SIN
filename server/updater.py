import InfluxBridge
import websocket
import asyncio
import datetime
import time
import json
import dateutil.parser
import pytz
import sys

# Action handlers for websocket. Currently unused.
def on_message(ws, message):
    sys.stderr.write(message)


def on_error(ws, error):
    sys.stderr.write(error)


def on_close(ws):
    sys.stderr.write("### closed ###")


def on_open(ws):
    pass


class Updater:
    """
    Class for automatic update of data from InfluxDB in django website.
    """
    def __init__(self):
        # Uncomment this if you are running Django server on localhost
        # self.sockaddr = "ws://localhost:8000/SIN"
        self.sockaddr = "ws://192.168.0.104:8080/SIN"
        tz = pytz.timezone('Europe/Prague')

        self.ws = websocket.WebSocket()
        self.bridge = InfluxBridge.InfluxBridge()
        self.last_time = datetime.datetime.now().replace(tzinfo=tz).astimezone(tz=tz)
        # Setting up websocket
        self.ws = websocket.WebSocket()
        self.ws.connect(self.sockaddr)
        # For debug purposes and test of the connection
        # self.ws.send(json.dumps({"value": "updater"}))
        self.ws.close()

    def run(self):
        """
        In an infinite loop, updater checks for new data and if there are any, sends them to frontend/Django
        """
        tz = pytz.timezone('Europe/Prague')
        while True:
            # Check for change
            new_temp = self.bridge.has_changed(measurement="temperature", known_last_time=self.last_time, duration="10m")
            new_hum = self.bridge.has_changed(measurement="humidity", known_last_time=self.last_time, duration="10m")
            new_data = {}
            # If there are new data, they are transformed into dictionary with signature of {"time": {}, "temperature": {}, "humidity":{}}
            if new_temp[0]:  # nova data ano
                self.last_time = datetime.datetime.now().astimezone(tz=tz).replace(tzinfo=tz)
                data = self.bridge.get_fields(new_temp[1], "time", "value")
                new_data["time"] = data["time"]
                new_data["temperature"] = data["value"]

            if new_hum[0]:  # nova data ano
                self.last_time = datetime.datetime.now().astimezone(tz=tz).replace(tzinfo=tz)
                data = self.bridge.get_fields(new_hum[1], "time", "value")
                new_data["time"] = data["time"]
                new_data["humidity"] = data["value"]

            # If there are some data ready to be sent, send them
            if new_data.keys():
                sys.stderr.write("New data being sent")
                self.ws.connect(self.sockaddr)
                self.ws.send(json.dumps(new_data))
                self.ws.close()

            time.sleep(10*60) # 10 minutes

    def get_last_time(self, data):
        """
        Helping function, gets the last ("biggest") time from InfluxDB-style formatted data
        :param data: InfluxDB-style formatted data
        :return: Last time.
        """
        tz = pytz.timezone('Europe/Prague')
        ret = dateutil.parser.parse(data[0]["time"]).astimezone(tz=tz).replace(tzinfo=tz)
        for item in data:
            t = dateutil.parser.parse(item["time"]).astimezone(tz=tz).replace(tzinfo=tz)
            if t > ret:
                ret = t
        sys.stderr.write("New last time: {}".format(ret))
        return ret


