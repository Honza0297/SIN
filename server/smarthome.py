#!/usr/bin/python3

import tempstation
import updater
import threading
import sys

if __name__ == "__main__":
    """
    These three objects have infinite loop to do their jobs - using threads to run them nicely.
    There is always an option to run every obj in "solo" mode. 
    """
    publisher = tempstation.TempstationPublisher()
    subscriber = tempstation.TempstationSubscriber()
    updater = updater.Updater()

    pub_thread = threading.Thread(target=publisher.continuous_publishing, kwargs={"period": 300}) # 300 seconds ~ 5 minutes request for temp and hum
    sub_thread = threading.Thread(target=subscriber.run)  # subscribing to tempstation-related topics and save the data to InfluxDB
    update_thread = threading.Thread(target=updater.run)  # Updating website

    try:
        pub_thread.start()
        sub_thread.start()
        update_thread.start()
    except:  # NOTE: Catch only needed exceptions
        sys.stderr.write("Threads failed.")

