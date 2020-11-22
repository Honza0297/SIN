#!/usr/bin/python3

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import datetime

MQTT_ADDRESS = '192.168.0.105'
MQTT_USER = 'jaberan'
MQTT_PASSWORD = 'temderku5j'
MQTT_TOPIC_MAIN = "home/#"


# noinspection SqlNoDataSourceInspection
class InfluxBridge:
    def __init__(self):
        self.client = InfluxDBClient(host='192.168.0.105', port=8086)

        created = False
        databases = self.client.get_list_database()
        for db in databases:
            if db["name"] == "smarthome":
                created = True
        if not created:
            self.client.create_database("smarthome")

        self.client.switch_database("smarthome")

    def store_data(self, measurement, value):
        self.client = InfluxDBClient(host='192.168.0.105', port=8086)
        self.client.switch_database("smarthome")
        self.client.write_points("{} value={}".format(measurement, value), database="smarthome", protocol="line")
        self.client.close()

    def has_changed(self, measurement, known_last_time):
        self.client = InfluxDBClient(host='192.168.0.105', port=8086)
        self.client.switch_database("smarthome")
        last_val = next(self.client.query("SELECT time, value FROM {} GROUP BY * ORDER BY DESC LIMIT 1".format(measurement)).get_points())
        db_last_time = datetime.datetime.strptime(last_val["time"], '%Y-%m-%dT%H:%M:%S.%fZ')
        return db_last_time > known_last_time, last_val

    def get_data(self, measurement, start=None, stop=None, aggregation=None):
        return self.client.query("select * from {measurement}")
