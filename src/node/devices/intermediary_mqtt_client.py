from node.devices import MQTTClient

class IntermediateMQTTClient(MQTTClient):
    def on_message_received(topic, payload, **kwargs):
        print("Received message from topic '{}': {}".format(topic, payload))
        
        # TODO: process received message and send to group 9

    def run(self):
        self.connect()

        self.subscribe("vehicles", callback=on_message_received)