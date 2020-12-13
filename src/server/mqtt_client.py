from node.devices.mqtt_client import MQTTClient
import config
import time


class ServerMQTTClient(MQTTClient):

    def __init__(self, connection):
        super().__init__(connection)
    

    def run(self):
        self.connect()

        def test_callback(topic, payload, **kwargs):
            print("Received message from topic '{}': {}".format(topic, payload))

        self.subscribe('vehicles', callback=test_callback)

        while True:
            print(f'the current my_vehicles is {str(config.my_vehicles)}')
            time.sleep(1)
