import speed_sensor, headway_sensor, wiper_controller#,mqtt_client
import light_controller, rainfall_sensor, photo_sensor
import communication_device,listener
from threading import Thread
import time


class Vehicle():

    def __init__(
        self, 
        x, 
        y,
        communication_device,
        listener,
        #mqtt_client,
        speed_sensor,
        #wiper_controller,
        #light_controller,
        headway_sensor,
        photo_sensor=None, 
        rainfall_sensor=None
    ):
        self.x = x
        self.y = y
        
        self.devices = []
        self.communication_device = communication_device
        self.devices.append(communication_device)
        self.listener = listener
        self.devices.append(listener)


        # self.mqtt_client = mqtt_client
        # self.devices.append(mqtt_client)

        self.speed_sensor = speed_sensor
        self.devices.append(speed_sensor)

        # self.wiper_controller = wiper_controller
        # self.devices.append(self.wiper_controller)

        # self.light_controller = light_controller
        # self.devices.append(self.light_controller)

        self.headway_sensor = headway_sensor
        self.devices.append(self.headway_sensor)

        if photo_sensor:
            self.photo_sensor = photo_sensor
            self.devices.append(self.photo_sensor)
        
        if rainfall_sensor:
            self.rainfall_sensor = rainfall_sensor
            self.devices.append(self.rainfall_sensor)


    def drive(self):

        for device in self.devices:
            device.start()
                
        while True:
            # this is where driving takes place
            pass

x=0 
y=0
communication_device = communication_device.aodv()
listener = listener.listener()
#mqtt_client=mqtt_client.MQTTClient()
speed_sensor=speed_sensor.SpeedSensor()
wiper_controller=wiper_controller.WiperController()
light_controller=light_controller.LightController()
headway_sensor=headway_sensor

V=Vehicle(x,y,communication_device,listener,#mqtt_client,
    speed_sensor,#wiper_controller,
    #light_controller,
    headway_sensor
    )
V.drive()
