import argparse

from iot_core.connections import MQTTConnection
from node.intermediary import Intermediary
from node.devices import MQTTClient
from node.devices import IntermediarySocketListener

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-host", help="hostname or ip of external p2p vehicular network")
    parser.add_argument("--remote-listen-port", help="port to listen to remote on",type=int)
    parser.add_argument("--remote-send-port", help="port on remote to send updates to",type=int)

    args = parser.parse_args()

    intermediary = Intermediary(
        mqtt_client=MQTTClient(MQTTConnection.get_mqtt_connection_over_websocket()),
        intermediary_socket_listener=IntermediarySocketListener(args.remote_host, args.remote_listen_port)
    )

    input("Press enter to close...")
