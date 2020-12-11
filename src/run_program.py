# this should the entry point of everything
import time
from iot_core.connections import MQTTConnection

if __name__ == "__main__":

    def test_callback(topic, payload, **kwargs):
        print("Received message from topic '{}': {}".format(topic, payload))

    new_connection = MQTTConnection()

    new_connection.connect()

    new_connection.subscribe('test-topic', callback=test_callback)

    for i in range(10):
        new_connection.publish('test-topic', f'wtf {i}')
        time.sleep(1)
