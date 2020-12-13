from node.devices.mqtt_client import MQTTClient
import time


class ServerMQTTClient(MQTTClient):

    def __init__(self, connection):
        super.__init__(self, connection)
    

    def run(self):
        self.connect()

        def test_callback(topic, payload, **kwargs):
            print("Received message from topic '{}': {}".format(topic, payload))

        self.subscribe('vehicles', callback=test_callback)

        while True:
            self.publish('vehicles', 'sfse')
            time.sleep(1)
