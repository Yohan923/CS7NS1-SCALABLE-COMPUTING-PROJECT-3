class Intermediary():
    """
    docstring
    """
    def __init__(
        self,
        mqtt_client,
        intermediary_socket_listener,
    ):
        self.mqtt_client=mqtt_client
        self.intermediary_socket_listener=intermediary_socket_listener

        print("Intermediary created")