# from config import my_vehicle
import json


def aggregate_full_vehicle_states():
    # payload = {
    #     'x': str(my_vehicle.x),
    #     'y': str(my_vehicle.y),
    #     'speed': str(my_vehicle.speed_sensor.get_speed())
    #     # add more later
    # }
    payload = {
        'x': 0,
        'y': 0,
        'speed': 0
    }
    return json.dumps(payload)