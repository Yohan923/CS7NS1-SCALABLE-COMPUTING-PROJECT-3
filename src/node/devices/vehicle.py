import speed_sensor, headway_sensor, wiper_controller#,mqtt_client
import light_controller, rainfall_sensor, photo_sensor
import communication_device,listener
from threading import Thread
import time
import socket,select,json

AODV_PORT=33880
SPEED_PORT=33881
HEADWAY_PORT=33882




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


        communication_device.set_node_id('1')
        self.communication_device = communication_device
        self.devices.append(communication_device)
        self.aodv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.aodv_sock.bind(('localhost', AODV_PORT))
        self.aodv_sock.setblocking(0)
        self.aodv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        listener.set_node_id('1')
        self.listener = listener
        self.devices.append(listener)

        # self.mqtt_client = mqtt_client
        # self.devices.append(mqtt_client)

        self.speed_sensor = speed_sensor
        self.devices.append(speed_sensor)
        self.speed_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.speed_sock.bind(('localhost', SPEED_PORT))
        self.speed_sock.setblocking(0)
        self.speed_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # self.wiper_controller = wiper_controller
        # self.devices.append(self.wiper_controller)

        # self.light_controller = light_controller
        # self.devices.append(self.light_controller)

        self.headway_sensor = headway_sensor
        self.devices.append(self.headway_sensor)
        self.headway_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.headway_sock.bind(('localhost', HEADWAY_PORT))
        self.headway_sock.setblocking(0)
        self.headway_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
            
            inputs = [self.speed_sock, self.headway_sock, self.aodv_sock]
            outputs = []
            
            # Run the main loop
            while inputs:
                readable, _, _ = select.select(inputs, outputs, inputs)
                for r in readable:
                    if r is self.speed_sock:
                        command, _ = self.speed_sock.recvfrom(100)
                        command = command.decode('utf-8')
                        print(command)
                        
                    elif r is self.headway_sock:
                        command, _ = self.headway_sock.recvfrom(1000)
                        command = command.decode('utf-8')
                        print(command)

                    elif r is self.aodv_sock:
                        # We got a message from the network
                        message, _ = self.aodv_sock.recvfrom(2000)
                        message = message.decode('utf-8')  
                        print(message)         
                

x=0 
y=0
communication_device = communication_device.aodv()
listener = listener.listener()
#mqtt_client=mqtt_client.MQTTClient()
speed_sensor=speed_sensor.SpeedSensor()
# wiper_controller=wiper_controller.WiperController()
# light_controller=light_controller.LightController()
headway_sensor=headway_sensor.HeadwaySensor()

V=Vehicle(x,y,communication_device,listener,#mqtt_client,
    speed_sensor,#wiper_controller,
    #light_controller,
    headway_sensor
    )
V.drive()
