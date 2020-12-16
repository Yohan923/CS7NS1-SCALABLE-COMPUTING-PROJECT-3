from awscrt import mqtt
import config
import json
import sys


# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback on server when data for vehicles are obtained

# {"id":id,"speed_x": 0.0, "acceleration_x": 0.0, "Xlocation": 0.0,
#        "speed_y": 0.0, "acceleration_y": 0.0, "Ylocation": 0.0,
#        "headway": 0,"wiper_speed": 0,"light": 0,'neighbors':[]}
def on_full_vehicles_states_received(topic, payload, **kwargs):
    payload = json.loads(payload)
    vehicle_id = payload['id']
    config.my_vehicles.update({vehicle_id: payload})


def on_rainfall_received(topic, payload, **kwargs):
    payload = json.loads(payload)
    rainfall = payload['rainfall']
    try:
        config.my_vehicle.wiper_controller.set_speed_by_rainfall(int(rainfall))
        config.my_vehicle.all_sensors['humidity'] = int(rainfall)
    except Exception:
        pass


def on_photointensity_received(topic, payload, **kwargs):
    payload = json.loads(payload)
    photointensity = payload['photointensity']
    try:
        config.my_vehicle.light_controller.set_speed_by_photo_intensity(int(photointensity))
        config.my_vehicle.all_sensors['light_intensity'] = int(photointensity)
    except Exception:
        pass


# Callback on mqtt when mesage received
def on_message_received(topic, payload, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    
    config.my_vehicle.intermediary_socket_writer.msg_send(payload)