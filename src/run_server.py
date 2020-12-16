import argparse
import json
from config import init_vehicles_dict_for_server
from server.mqtt_client import ServerMQTTClient
from iot_core.connections import MQTTConnection


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--cert', help="File path to your client certificate, in PEM format.")
    parser.add_argument('--key', help="File path to your private key, in PEM format.")
    args = parser.parse_args()

    init_vehicles_dict_for_server()
    
    mqtt_client = ServerMQTTClient(MQTTConnection.get_mqtt_connection(args.cert, args.key))
    mqtt_client.start()

    while True:
        inputs = input('How can I help you my master: ')
        if 'rainfall' in inputs:
            try:
                mqtt_client.publish('rainfall', json.dumps({'rainfall': int(inputs.split('=')[1])}))
            except Exception:
                print('oops something is wrong when publishing')
        elif 'photointensity' in inputs:
            try:
                mqtt_client.publish('photointensity', json.dumps({'photointensity': int(inputs.split('=')[1])}))
            except Exception:
                print('oops something is wrong when publishing')

