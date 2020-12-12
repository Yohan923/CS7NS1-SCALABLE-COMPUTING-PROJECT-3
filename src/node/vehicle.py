from node.devices import SpeedSensor, HeadwaySensor, WiperController, LightController, RainfallSensor, PhotoSensor
from threading import Thread
import time


class Vehicle(Thread):

    def __init__(
        self, 
        x, 
        y,
        mqtt_client,
        speed_sensor,
        wiper_controller,
        light_controller,
        headway_sensor,
        photo_sensor=None, 
        rainfall_sensor=None
    ):
        Thread.__init__(self)
        self.x = x
        self.y = y
        
        self.devices = []
        # self.communication_device = 

        self.mqtt_client = mqtt_client
        self.devices.append(mqtt_client)

        self.speed_sensor = speed_sensor
        self.devices.append(speed_sensor)

        self.wiper_controller = wiper_controller
        self.devices.append(self.wiper_controller)

        self.light_controller = light_controller
        self.devices.append(self.light_controller)

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

        def test_callback(topic, payload, **kwargs):
            print("Received message from topic '{}': {}".format(topic, payload))

        self.mqtt_client.subscribe('test-topic', callback=test_callback)

        for i in range(10):
            self.mqtt_client.publish('test-topic', f'wtf {i}')
            time.sleep(1)
                
        while True:
            # this is where driving takes place
            pass