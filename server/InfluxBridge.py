#!/usr/bin/python3

from influxdb import InfluxDBClient
import dateutil.parser
import pytz
import sys

#MQTT related constants
MQTT_ADDRESS = '192.168.0.105'
MQTT_USER = 'jaberan'
MQTT_PASSWORD = 'temderku5j'
MQTT_TOPIC_MAIN = "home/#"


class InfluxBridge:
    """
    Class works as an adapter between InfluxDB and the rest of the system.
    NOTE: Not fully implemented.
    """
    def __init__(self):
        self.client = InfluxDBClient(host='192.168.0.105', port=8086)

        # Checks of smarthome DB exists and creates/connects to it
        created = False
        databases = self.client.get_list_database()
        for db in databases:
            if db["name"] == "smarthome":
                created = True
        if not created:
            self.client.create_database("smarthome")

        self.client.switch_database("smarthome")

    # Method is used to store data into DB
    def store_data(self, measurement, value):
        self.client = InfluxDBClient(host='192.168.0.105', port=8086)
        self.client.switch_database("smarthome")
        self.client.write_points("{} value={}".format(measurement, value), database="smarthome", protocol="line")
        self.client.close()

    # Checks of there are any new data from last time and if there are any, it returns them aggregation by time period
    def has_changed(self, measurement, known_last_time, duration):
        tz = pytz.timezone('Europe/Prague')
        self.client = InfluxDBClient(host='192.168.0.105', port=8086)
        self.client.switch_database("smarthome")

        last_val = next(self.client.query("SELECT time, value FROM {} GROUP BY * ORDER BY DESC LIMIT 1".format(measurement)).get_points())
        db_last_time = dateutil.parser.parse(last_val["time"]).astimezone(tz=tz).replace(tzinfo=tz)
        sys.stderr.write("LOG: db_last, known_last: {} {} {}".format(db_last_time, known_last_time, db_last_time > known_last_time))
        data = None

        if db_last_time > known_last_time:
            sys.stderr.write("LOG: bridge nova data ano")
            data = self.get_data(measurement=measurement, start=known_last_time, aggregation=duration)
        return db_last_time > known_last_time, data

    # gets only desired fields in the format which fronted can understand (like {"time": {}, "temperature": {}, "humidity":{}})
    def get_fields(self, source, *fields):
        return_data = dict.fromkeys(fields)
        for key in return_data.keys():
            return_data[key] = list()
        if source is dict:
            source = [source]
        for record in source:
            for field in fields:
                if field == "time":
                    return_data[field].append(dateutil.parser.parse(record[field]).strftime("%d.%m, %H:%M"))
                else:
                    return_data[field].append(record[field])
        return return_data

    # Function gets aggregated data from start time aggregated by time period
    def get_aggregated_data(self, measurement, fields, start, aggregation):
        if start:
            time = start.astimezone(tz=pytz.timezone("UTC")).replace(tzinfo=pytz.timezone("UTC")).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            data = [item for item in self.client.query("select mean({}) from {} where time < \'{}\' group by time({}) fill(none)".format(fields, measurement, time, aggregation)).get_points()]
        else:
            data = [item for item in self.client.query("select mean({}) from {} group by time({}) fill(none)".format(fields, measurement, aggregation)).get_points()]
        for dato in data:
            # Check if influx does not name mean(value) as mean - it most probably does!

            keys = dato.keys()
            new_keys = list()
            old_keys = list()
            for key in keys:
                if key.startswith("mean_"):
                    new_keys.append(key[5:])
                    old_keys.append((key))

            for i in range(len(old_keys)):
                dato[new_keys[i]] = dato[old_keys[i]]
                dato.pop(old_keys[i])

        return data

    # Function gets data. There can be specified fields, time from and to and aggregation
    def get_data(self, measurement, fields="*", start=None, stop=None, aggregation=None):
        if aggregation:
            return self.get_aggregated_data(measurement, fields, start, aggregation)
        if start:
            time = start.astimezone(tz=pytz.timezone("UTC")).replace(tzinfo=pytz.timezone("UTC")).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            print("LOG: query is: ", "select {} from {} where time > \'{}\'".format(fields, measurement, time))
            return [item for item in self.client.query("select {} from {} where time > \'{}\'-1m59s700ms".format(fields, measurement, time)).get_points()] # -2m je vyrovnani timezony 00:58 a 01:00
        else:
            return [item for item in self.client.query("select {} from {}".format(fields, measurement)).get_points()]

