from node.devices import SpeedSensor, HeadwaySensor, WiperController, LightController, RainfallSensor, PhotoSensor
from node.devices import IntermediarySocketListener, IntermediarySocketWriter
from node.devices import CommunicationDevice
from threading import Thread
import socket,select,json,time
from threading import Thread
import time
import sys,re
import os




VEHICLE_PORT=33100
AODV_PORT = 33880
AODV_THREAD_PORT = 33980
SPEED_PORT=33881
SPEED_THREAD_PORT = 33981
HEADWAY_PORT=33882
HEADWAY_THREAD_PORT=33982
WIPER_PORT=33883
WIPER_THREAD_PORT=33983
LIGHT_PORT=33884
LIGHT_THREAD_PORT=33984
PHOTO_PORT = 33885
PHOTO_THREAD_PORT = 33985
RAINFALL_PORT = 33886
RAINFALL_THREAD_PORT = 33986 
AODV_NETWORK_PORT = 33300 
AODV_SPEED_PORT=33500



class Vehicle():

    def __init__(
        self, 
        id,
        communication_device,
        #listener,
        speed_sensor,
        wiper_controller,
        light_controller,
        headway_sensor,
        mqtt_client=None,
        photo_sensor=None, 
        rainfall_sensor=None,
        intermediary_socket_listener=None,
        intermediary_socket_writer=None
    ):
        self.all_sensors={"id":id,"speed": 0.0, "acceleration": 0.0, "location": 0.0,
        "lane":0,"direction":0,
        "headway": 0,"wiper_speed": 0,"light": 0,'neighbors':[]}
        
        self.devices = []
        self.inputs =[]
        
        if intermediary_socket_listener:
            self.intermediary_socket_listener = intermediary_socket_listener
            self.devices.append(intermediary_socket_listener)
        else:
            self.intermediary_socket_listener = None
        
        if intermediary_socket_writer:
            self.intermediary_socket_writer = intermediary_socket_writer
        else:
            self.intermediary_socket_writer = None

        self.communication_device = communication_device
        self.devices.append(communication_device)
        self.aodv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.aodv_sock.bind(('localhost', AODV_PORT))
        self.aodv_sock.setblocking(0)
        self.aodv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.inputs.append(self.aodv_sock)

        if mqtt_client:
            self.mqtt_client = mqtt_client
            self.devices.append(mqtt_client)

        self.speed_sensor = speed_sensor
        self.devices.append(speed_sensor)
        self.speed_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.speed_sock.bind(('localhost', SPEED_PORT))
        self.speed_sock.setblocking(0)
        self.speed_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.inputs.append(self.speed_sock)

        self.wiper_controller = wiper_controller
        self.devices.append(self.wiper_controller)
        self.wiper_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.wiper_sock.bind(('localhost', WIPER_PORT))
        self.wiper_sock.setblocking(0)
        self.wiper_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.inputs.append(self.wiper_sock)

        self.light_controller = light_controller
        self.devices.append(self.light_controller)
        self.light_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.light_sock.bind(('localhost', LIGHT_PORT))
        self.light_sock.setblocking(0)
        self.light_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.inputs.append(self.light_sock)

        self.headway_sensor = headway_sensor
        self.devices.append(self.headway_sensor)
        self.headway_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.headway_sock.bind(('localhost', HEADWAY_PORT))
        self.headway_sock.setblocking(0)
        self.headway_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.inputs.append(self.headway_sock)

        if photo_sensor:
            self.photo_sensor = photo_sensor
            self.devices.append(self.photo_sensor)
            self.photo_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.photo_sock.bind(('localhost', PHOTO_PORT))
            self.photo_sock.setblocking(0)
            self.photo_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)            
            self.inputs.append(self.photo_sock)
   
        if rainfall_sensor:
            self.rainfall_sensor = rainfall_sensor
            self.devices.append(self.rainfall_sensor)
            self.rainfall_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.rainfall_sock.bind(('localhost', RAINFALL_PORT))
            self.rainfall_sock.setblocking(0)
            self.rainfall_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
            self.inputs.append(self.rainfall_sock)
        


    def update(self,message,keys):
        for k in keys:
            self.all_sensors[k]=message[k]

    def aggregate_full_vehicle_states(self):
        return json.dumps(self.all_sensors)

    def get_full_vehicle_states(self):
        return self.all_sensors

    def drive(self):

        for device in self.devices:
            device.start()

        while True:
            
            # inputs = [self.speed_sock, self.headway_sock, self.aodv_sock,self.wiper_sock,self.light_sock,self.photo_sock,self.rainfall_sock]
            outputs = []
            
            # Run the main loop
            while self.inputs:
                readable, _, _ = select.select(self.inputs, outputs, self.inputs)
                for r in readable:
                    if r is self.speed_sock:
                        message, _ = self.speed_sock.recvfrom(2000)
                        message = message.decode('utf-8')
                        message = json.loads(message)
                        # print(message)
                        keys = ["speed", "acceleration","location",
                        "lane", "direction"]
                        self.update(message,keys)

                        
                    elif r is self.headway_sock:
                        message, _ = self.headway_sock.recvfrom(1000)
                        message = message.decode('utf-8')
                        message = json.loads(message)
                        # print(message)
                        keys = ["headway"]
                        self.update(message,keys)

                    elif r is self.aodv_sock:
                        # We got a message from the network
                        command, _ = self.aodv_sock.recvfrom(2000)
                        command = command.decode('utf-8')  
                        commands = re.split('\'',command)
                        message = {}
                        # print(commands[1])
                        temp=commands[2]
                        # print(temp[2:-2])
                        message[commands[1]]=int(temp[1:-2])

                        if "neighbors" in message.keys():
                            keys = ["neighbors"]
                            self.update(message,keys)
                        elif "humidity" in message.keys():
                            print("aodv->main "+str(message["humidity"]))
                            keys = ["humidity"]
                            self.update(message,keys)
                            self.aodv_sock.sendto(bytes(command, 'utf-8'), 0, ('localhost', WIPER_THREAD_PORT))
                        elif "light_intensity" in message.keys():
                            print("aodv->main "+str(message["light_intensity"]))
                            keys = ["light_intensity"]
                            self.update(message,keys)
                            self.aodv_sock.sendto(bytes(command, 'utf-8'), 0, ('localhost', LIGHT_THREAD_PORT))

                    elif r is self.wiper_sock:
                        message, _ = self.wiper_sock.recvfrom(2000)
                        message = message.decode('utf-8')  
                        message = json.loads(message)
                        # print(message)
                        keys = ["wiper_speed"]
                        self.update(message,keys)

                    elif r is self.light_sock:
                        message, _ = self.light_sock.recvfrom(2000)
                        message = message.decode('utf-8')  
                        message = json.loads(message)
                        # print(message)
                        keys = ["light"]
                        self.update(message,keys)

                    elif r is self.photo_sock:
                        message, _ = self.photo_sock.recvfrom(2000)
                        message = message.decode('utf-8')  
                        message = json.loads(message)
                        # print(message)
                        keys = ["light_intensity"]
                        self.update(message,keys)

                        

                    elif r is self.rainfall_sock:
                        message, _ = self.rainfall_sock.recvfrom(2000)
                        message = message.decode('utf-8')  
                        message = json.loads(message)
                        # print(message)
                        keys = ["humidity"]
                        self.update(message,keys)                        
