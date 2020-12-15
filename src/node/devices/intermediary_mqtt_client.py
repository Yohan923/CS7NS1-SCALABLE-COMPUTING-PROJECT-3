from node.devices import MQTTClient

class IntermediateMQTTClient(MQTTClient):
    def on_message_received(topic, payload, **kwargs):
        print("Received message from topic '{}': {}".format(topic, payload))
        
        # TODO: process received message and send to group 9

    def subscribe(self, topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=None):
        print("Subscribing to topic '{}'...".format(topic))
        subscribe_future, packet_id = self._connection.subscribe(
            topic=topic,
            qos=qos,
            callback=callback)

        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(str(subscribe_result['qos'])))
        return packet_id