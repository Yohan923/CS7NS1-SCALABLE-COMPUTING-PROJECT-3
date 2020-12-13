# this should the entry point of everything
import time
from config import init
from iot_core.connections import MQTTConnection
from node.devices.mqtt_client import MQTTClient
from node.devices.headway_sensor import HeadwaySensor
from node.devices.speed_sensor import SpeedSensor
from node.devices.communication_device import CommunicationDevice
from node.devices.wiper_controller import WiperController, WIPER_SPEED
from node.devices.light_controller import LightController, LIGHT_INTENSITY
from node.vehicle import Vehicle
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("nid", help="enter node id",type=int)
    parser.add_argument("--neighbors", help="enter neighbors", nargs='+')
    parser.add_argument("--xLoc", help="enter initial x location")
    parser.add_argument("--yLoc", help="enter initial y location")    
    parser.add_argument("--init_speed_x", help="enter initial speed in x direction")
    parser.add_argument("--init_speed_y", help="enter initial speed in y direction")


    args = parser.parse_args()

    vehicle = Vehicle(
        communication_device=CommunicationDevice(args.nid,args.neighbors),
        mqtt_client=MQTTClient(MQTTConnection.get_mqtt_connection_over_websocket()),
        speed_sensor=SpeedSensor(), 
        wiper_controller=WiperController(WIPER_SPEED.SLOW), 
        light_controller=LightController(LIGHT_INTENSITY.NORMAL),
        headway_sensor=HeadwaySensor(23)
        )

    init(vehicle) # import config file in other modules and use config.my_vehicle to access the vehicle

    vehicle.drive()

