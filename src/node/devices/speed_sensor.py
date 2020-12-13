import threading
import time
import sys, socket, time
import logging,re,random

import json
delta_t=0.1#0.1s
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
AODV_NETWORK_PORT = 33300 
AODV_SPEED_PORT=33500


class SpeedSensor(threading.Thread):
    
    def __init__(self,loc,lane,speed,acc):
        threading.Thread.__init__(self)
        self.sock = SPEED_THREAD_PORT
        self.port = 0
        self.aodv_tester_port = 33500


        self.SPEED = speed
        self.ACCELERATION = acc
        self.LOC = loc
        self.LANE = lane
        self.DIRECTION = int(loc/100)
        self.STATUS = "ACTIVE"

        
    def send(self, message):
        self.sock.sendto(message, 0, ('localhost', AODV_SPEED_PORT))
        self.sock.sendto(message, 0, ('localhost', SPEED_PORT))

    def broadcast_packet(self):
        return

    def construct_packet(self,keys, values):
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return json.dumps(packet)



    def update(self):
        if self.STATUS == "ACTIVE":
            self.LOC += (self.SPEED * 1)%400
            if self.SPEED < 10:
                self.SPEED += self.ACCELERATION * 1

            # Some checks to make sure car isn't reversing, or is stationary for too long, etc..
            if self.SPEED < 0:
                self.SPEED = 0
            elif self.SPEED > 10:
                self.SPEED = 10
                self.ACCELERATION = 0


        keys = ["speed", "location","acceleration","lane","direction"]
        values = [self.SPEED, self.LOC,self.ACCELERATION, self.LANE,self.DIRECTION]

        myPacket = self.construct_packet(keys, values)
        return myPacket


    # Default action handler
    def command_default(self):
        pass


    # Thread start routine
    def run(self):
        print("speed and location sensor start")      
        
        
        # Setup socket to communicate with the AODV protocol handler thread
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))
        self.sock.setblocking(0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        
        while (True):
            # send
            myPacket = self.update()
            myPacket_bytes = bytes(myPacket, 'utf-8')
            self.send(myPacket_bytes)

            # receive
            try:
                command, _ = self.sock.recvfrom(100)
                command = command.decode('utf-8')
                command = re.split(':', command)
                command_type = command[0]
                self.command = command
                print(command_type)

                if command_type == "CHANGE_LANE":
                    self.lane = (self.lane+1)%2
                else:
                    self.command_default()

            except:
                pass  

            

            time.sleep(1)



