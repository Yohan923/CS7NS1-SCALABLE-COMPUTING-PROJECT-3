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
    parser.add_argument("--location", help="enter initial x location",type=float,default=0)
    parser.add_argument("--lane", help="enter current lane id",type=int,default=0)
    parser.add_argument("--status", help="enter vehicle status, active=1, inactive=0",type=int,default=1)
    parser.add_argument("--speed", help="enter initial speed ",type=float,default=0)
    parser.add_argument("--acceleration", help="enter initial acceleration",type=float,default=3)
    parser.add_argument("--photo_sensor", help="set light intensity. Set this to zero if no photo_sensor",default=0)
    parser.add_argument("--rainfall_sensor", help="set humidity. Set this to zero if no rainfall_sensor",default=0)

    args = parser.parse_args()

    if args.photo_sensor !=0:
        photo_sensor=PhotoSensor(args.photo_sensor)
    else:
        photo_sensor=None, 
    if args.rainfall_sensor !=0:
        rainfall_sensor=RainfallSensor(args.rainfall_sensor)
    else:
        rainfall_sensor=None, 


    vehicle = Vehicle(
        id=args.nid,
        communication_device=CommunicationDevice(args.nid,args.neighbors),
        mqtt_client=MQTTClient(MQTTConnection.get_mqtt_connection_over_websocket()),
        speed_sensor=SpeedSensor(args.nid,args.location,args.lane,args.speed,args.acceleration,status=args.status), 
        wiper_controller=WiperController(WIPER_SPEED.SLOW), 
        light_controller=LightController(LIGHT_INTENSITY.NORMAL),
        headway_sensor=HeadwaySensor(23),
        photo_sensor=photo_sensor, 
        rainfall_sensor=photo_sensor
        )

    init(vehicle) # import config file in other modules and use config.my_vehicle to access the vehicle

    vehicle.drive()

