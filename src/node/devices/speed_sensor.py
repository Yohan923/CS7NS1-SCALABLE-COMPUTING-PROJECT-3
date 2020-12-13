import threading
import time
import sys, socket, time
import logging,re,random
from opensimplex import OpenSimplex
import json
delta_t=0.1#0.1s
SPEED_PORT=33881
AODV_SPEED_PORT=33500
SPEED_THREAD_PORT = 33981


class SpeedSensor(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = SPEED_THREAD_PORT
        self.port = 0
        self.aodv_tester_port = 33500


        self.SPEED_X = random.randrange(100)
        self.ACCELERATION_X = random.randint(-3, 6)
        self.SPEED_Y = random.randrange(100)
        self.ACCELERATION_Y = random.randint(-3, 6)
        self.XLOC = 0.0
        self.YLOC = 0.0
        self.NOISE_COUNTER_INCREMENT = 0.1# Increasing this value would mean moving faster accross perlin noise space, meaning the difference between each value would be greater.
        self.noise_counter =0
        self.STATUS = "ACTIVE"

        
    def send(self, message):
        self.sock.sendto(message, 0, ('localhost', AODV_SPEED_PORT))
        self.sock.sendto(message, 0, ('localhost', SPEED_PORT))

    # TODO: broadcast the packet?
    def broadcast_packet(self):
        return

    def construct_packet(self,keys, values):
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return json.dumps(packet)



    def update(self,accelleration_change):
        if self.STATUS == "ACTIVE":
            self.ACCELERATION_Y += accelleration_change
            self.ACCELERATION_X += accelleration_change
            self.YLOC += self.SPEED_Y * 0.1
            self.SPEED_Y += self.ACCELERATION_Y * 0.1
            self.XLOC += self.SPEED_X * 0.1
            self.SPEED_X += self.ACCELERATION_X * 0.1

            # Some checks to make sure car isn't reversing, or is stationary for too long, etc..
            if self.SPEED_Y < 0:
                self.SPEED_Y = 0
            elif self.SPEED_Y > 180:
                self.SPEED_Y = 180
            if self.ACCELERATION_Y < -5:
                self.ACCELERATION_Y = -5
            elif self.ACCELERATION_Y > 5:
                self.ACCELERATION_Y = 5

            self.noise_counter += self.NOISE_COUNTER_INCREMENT
        # TODO: change this
        elif self.STATUS == "STOPPING":
            self.SPEED_Y = 0;
            self.ACCELERATION_Y =0;

        keys = ["speed_x", "acceleration_x","Xlocation",
        "speed_y", "acceleration_y","Ylocation","status"]
        values = [self.SPEED_X, self.ACCELERATION_X, self.XLOC,
        self.SPEED_Y, self.ACCELERATION_Y, self.YLOC,self.STATUS]

        # I guess we make this packet available to gram from some port?
        myPacket = self.construct_packet(keys, values)
        return myPacket


    # Default action handler
    def command_default(self):
        pass


    # Thread start routine
    def run(self):
        print("speed and location sensor start")
        with open('speed.txt', 'w') as f:
            f.write('speed_x,acceleration_y,Ylocation,status\n')       
        
        noise = OpenSimplex()
        
        # Setup socket to communicate with the AODV protocol handler thread
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))
        self.sock.setblocking(0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        
        while (True):
            # send
            noise = OpenSimplex()
            accelleration_change = noise.noise2d(self.noise_counter, 0)
            myPacket = self.update(accelleration_change)
            with open('speed.txt', 'a') as f:
                f.write(myPacket+"\n")
            sensor_type="LOCATION"
            myPacket=sensor_type+":"+myPacket
            myPacket_bytes = bytes(myPacket, 'utf-8')
            self.send(myPacket_bytes)

            # receive
            try:
                command, _ = self.sock.recvfrom(100)
                command = command.decode('utf-8')
                command = re.split(':', command)
                command_type = command[0]
                self.command = command

                if command_type == "COMMAND_STOP":
                    self.STATUS = "STOPPING"
                else:
                    self.command_default()

            except:
                pass  

            

            time.sleep(3)



