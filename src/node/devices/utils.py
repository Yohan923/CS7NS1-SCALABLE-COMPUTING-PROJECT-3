import config
import json


def aggregate_full_vehicle_states():
    # payload = {
    #     'x': str(my_vehicle.x),
    #     'y': str(my_vehicle.y),
    #     'speed': str(my_vehicle.speed_sensor.get_speed())
    #     # add more later
    # }
    payload = {
        'x': str(config.my_vehicle.x),
        'y': str(config.my_vehicle.y),
        'speed': str(config.my_vehicle.speed_sensor.get_speed())
        # add more later
    }
    return json.dumps(payload)