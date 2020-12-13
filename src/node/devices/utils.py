import config
import json


def aggregate_full_vehicle_states():
<<<<<<< HEAD

    return my_vehicle.aggregate_full_vehicle_states();
=======
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
>>>>>>> 70c15cb1170d526fe923bffa7a6c2e80721e45b5
