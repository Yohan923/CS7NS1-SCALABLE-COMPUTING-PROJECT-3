def init(vehicle):
    global my_vehicle # the whole project can now access the vehicle created at the start
    my_vehicle = vehicle


def init_vehicles_dict_for_server():
    global my_vehicles # the whole project can now access the vehicle created at the start
    my_vehicles = dict()