import speed_sensor, headway_sensor, wiper_controller#,mqtt_client
import light_controller, rainfall_sensor, photo_sensor
import communication_device,listener
from threading import Thread
import time
import socket,select,json

VEHICLE_PORT=33100
LIGHT_PORT=33884
LIGHT_THREAD_PORT=33984
WIPER_PORT=33883
WIPER_THREAD_PORT=33983
SPEED_PORT=33881
SPEED_THREAD_PORT = 33981
HEADWAY_PORT=33882
HEADWAY_THREAD_PORT=33982
AODV_PORT = 33880
AODV_THREAD_PORT = 33980
AODV_THREAD_SPEED_PORT=33500
AODV_SPEED_PORT=33400



class Vehicle():

    def __init__(
        self, 
        communication_device,
        #listener,
        #mqtt_client,
        speed_sensor,
        wiper_controller,
        light_controller,
        headway_sensor,
        photo_sensor=None, 
        rainfall_sensor=None
    ):
        self.all_sensors={"speed_x": 0.0, "acceleration_x": 0.0, "Xlocation": 0.0,
        "speed_y": 0.0, "acceleration_y": 0.0, "Ylocation": 0.0,
        "headway": 0,"wiper_speed": 0,"light": 0}
        
        self.devices = []

        communication_device.set_node_id('1')
        self.communication_device = communication_device
        self.devices.append(communication_device)
        self.aodv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.aodv_sock.bind(('localhost', AODV_PORT))
        self.aodv_sock.setblocking(0)
        self.aodv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


        # self.mqtt_client = mqtt_client
        # self.devices.append(mqtt_client)

        self.speed_sensor = speed_sensor
        self.devices.append(speed_sensor)
        self.speed_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.speed_sock.bind(('localhost', SPEED_PORT))
        self.speed_sock.setblocking(0)
        self.speed_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.wiper_controller = wiper_controller
        self.devices.append(self.wiper_controller)
        self.wiper_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.wiper_sock.bind(('localhost', WIPER_PORT))
        self.wiper_sock.setblocking(0)
        self.wiper_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.light_controller = light_controller
        self.devices.append(self.light_controller)
        self.light_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.light_sock.bind(('localhost', LIGHT_PORT))
        self.light_sock.setblocking(0)
        self.light_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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

    def update(self,message,keys):
        for k in keys:
            all_sensors[k]=message[k]





    def drive(self):

        for device in self.devices:
            device.start()
        while True:
            
            inputs = [self.speed_sock, self.headway_sock, self.aodv_sock,self.wiper_sock,self.light_sock]
            outputs = []
            
            # Run the main loop
            while inputs:
                readable, _, _ = select.select(inputs, outputs, inputs)
                for r in readable:
                    if r is self.speed_sock:
                        message, _ = self.speed_sock.recvfrom(2000)
                        message = message.decode('utf-8')
                        message = json.loads(message)
                        print(message)
                        keys = ["speed_x", "acceleration_x","Xlocation","speed_y", "acceleration_y","Ylocation"]
                        self.update(message,keys)

                        
                    elif r is self.headway_sock:
                        message, _ = self.headway_sock.recvfrom(1000)
                        message = message.decode('utf-8')
                        print(message)
                        message = json.loads(message)
                        print(message)
                        keys = ["headway"]
                        self.update(message,keys)

                    elif r is self.aodv_sock:
                        # We got a message from the network
                        message, _ = self.aodv_sock.recvfrom(2000)
                        message = message.decode('utf-8')  
                        print(message)     

                    elif r is self.wiper_sock:
                        message, _ = self.wiper_sock.recvfrom(2000)
                        message = message.decode('utf-8')  
                        print(message)  
                        message = json.loads(message)
                        print(message)
                        keys = ["wiper_speed"]
                        self.update(message,keys)

                    elif r is self.light_sock:
                        message, _ = self.light_sock.recvfrom(2000)
                        message = message.decode('utf-8')  
                        print(message)  
                        message = json.loads(message)
                        print(message)
                        keys = ["light"]
                        self.update(message,keys)



communication_device = communication_device.aodv()
#listener = listener.listener()
#mqtt_client=mqtt_client.MQTTClient()
speed_sensor=speed_sensor.SpeedSensor()
wiper_controller=wiper_controller.WiperController(1)
light_controller=light_controller.LightController(1)
headway_sensor=headway_sensor.HeadwaySensor()

V=Vehicle(x,y,communication_device,#listener,#mqtt_client,
    speed_sensor,wiper_controller,
    light_controller,
    headway_sensor
    )
V.drive()
