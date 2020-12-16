from awscrt import mqtt
import consts.iot_core as conf
# from node.devices.utils import aggregate_full_vehicle_states
import config
from threading import Thread
import time
import datetime
import json
from iot_core import callbacks


class MQTTClient(Thread):

    def __init__(self, connection):
        Thread.__init__(self)
        self._connection = connection

    def connect(self):
        print("Connecting to {} with client ID '{}'...".format(
        conf.ENDPOINT, conf.CLIENT_ID))
        connect_future = self._connection.connect()
        
        # Future.result() waits until a result is available
        connect_future.result()
        print("Connected!")


    def disconnect(self):
        # Disconnect
        print("Disconnecting...")
        disconnect_future = self._connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")


    def subscribe(self, topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=None):
        print("Subscribing to topic '{}'...".format(topic))
        subscribe_future, packet_id = self._connection.subscribe(
            topic=topic,
            qos=qos,
            callback=callback)

        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(str(subscribe_result['qos'])))
        return packet_id

    
    def publish(self, topic, message, qos=mqtt.QoS.AT_LEAST_ONCE):
        if not topic:
            print('topic is not specified for publish')
            return

        #print(f'Publishing message to topic = {topic}: {message}')
        self._connection.publish(
            topic=topic,
            payload=message,
            qos=qos)


    def run(self):
        self.connect()
        try:
            if config.my_vehicle.intermediary_socket_writer:
                self.subscribe("vehicles", callback=callbacks.on_message_received)

            self.subscribe('rainfall', callback=callbacks.on_rainfall_received)
            self.subscribe('photointensity', callback=callbacks.on_photointensity_received)
        except:
            pass
        while True:
            payload = config.my_vehicle.all_sensors
            payload['id'] = str(payload['id'])
            now = datetime.datetime.utcnow().isoformat(timespec='seconds')
            payload.update({'datetime': now})

            self.publish('vehicles', json.dumps(payload))
            time.sleep(1)
