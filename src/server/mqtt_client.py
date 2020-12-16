from node.devices.mqtt_client import MQTTClient
from iot_core.callbacks import on_full_vehicles_states_received
import config
import time


class ServerMQTTClient(MQTTClient):

    def __init__(self, connection):
        super().__init__(connection)
    

    def run(self):
        self.connect()

        self.subscribe('vehicles', callback=on_full_vehicles_states_received)

        while True:
            pass
