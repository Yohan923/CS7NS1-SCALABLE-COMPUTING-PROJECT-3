import threading
import time
import numpy as np
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

TIME_INTERVAL=0.1
MAX_ACCELERATION = 2
MIN_ACCELERATION = -2 
MAX_SPEED = 10
TOTAL_LENGHT = 400



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
        self.is_running = True

        # print("Initializing track\n")
        # self.nieghbours={}
        # self.track = Track()
        # self.myself = Car( Stats( (self.LOC,self.LANE), self.SPEED, self.ACCELERATION ), track=self.track)
        # self.track.Add(self.myself)
        
        
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
        self.ControlSpeedAndAcceleration()
        if self.STATUS == "ACTIVE":
            prev_loc = self.LOC
            self.LOC = int( prev_loc + (self.SPEED*step) )%400 

            self.SPEED = self.SPEED + (self.ACCELERATION*step)
            self.SPEED = max (0, self.SPEED)

        self.myself.update((self.LOC,self.LANE), self.SPEED, self.ACCELERATION )

        keys = ["speed", "location","acceleration","lane","direction"]
        values = [self.SPEED, self.LOC,self.ACCELERATION, self.LANE,self.DIRECTION]

        myPacket = self.construct_packet(keys, values)
        return myPacket


    # Default action handler
    def command_default(self):
        pass

    def Stop(self):
        self.is_running = False

    def SwitchLanes(self):
        self.LANE = (self.LANE+1)%2

    def findNearest(self):
        min=500
        nearestNode=""
        for sender in self.neighbours.keys():
            distance = abs(self.neighbours[sender]['location']-self.LOC)
            if distance<min:
                nearestNode=sender
        return nearestNode




    def ControlSpeedAndAcceleration(self):
        # nei = self.track.GetNieghbbours(self.myself)
        if(self.neighbours!={}):
            closest_car = self.neighbours[self.findNearest]
            self.LANE = 1-closest_car['lane']
            if(self.LOC < closest_car['location']):
                self.stats.acceleration = MAX_ACCELERATION
            else:
                self.ACCELERATION = MIN_ACCELERATION
        
        elif(self.SPEED < (MAX_SPEED)):
            self.ACCELERATION = MAX_ACCELERATION
        
        elif(self.SPEED > (MAX_SPEED)):
            self.ACCELERATION = MIN_ACCELERATION

    def onReceive(self,sender,msg):
        data = json.loads(msg)
        
        if (sender in self.neighbours.keys()):
            self.neighbours[sender]['location']=data['location'];
            self.neighbours[sender]['lane'] = data['lane']; 
            self.neighbours[sender]['speed']=data['speed']; 
            self.neighbours[sender]['acceleration']=data['acceleration'];
        else:
            self.nieghbours[sender] = data

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
                command, _ = self.sock.recvfrom(1000)
                command = command.decode('utf-8')
                command = re.split(':', command)
                command_type = command[0]
                self.command = command
                print(command_type)

                if command_type == "RECEIVE":
                    self.onReceive(command[1],command[2])
                else:
                    self.command_default()

            except:
                pass  
            time.sleep(TIME_INTERVAL)





class Stats:
    
    def __init__(self, location=(0,0), speed=0, acceleration=0):
        self.location = location
        self.speed = speed
        self.acceleration = acceleration

        
    def __str__(self):
        _str = "[{}  {}  {}]".format(self.location, self.speed, self.acceleration)
        return _str
    
    
class Track:
    
    def __init__(self, length = TOTAL_LENGHT):
        
        print("Initializing track\n")
        self.track = np.zeros((length, 2))
        self.cars = {}
        self.i_cars = 1
        self.is_running = True
        
    def __str__(self):
        spots_occupied = np.argwhere(self.track!=0)[:, 0].ravel()
        _str = "[TRACK {}]  ".format(spots_occupied)
        for car in self.cars.keys():
            _str = _str + "{}: {} , ".format(self.cars[car], car.stats)
        return _str
        
    def Add(self, car):
        self.cars[car] = self.i_cars 
        self.track[car.stats.location[0], car.stats.location[1]] = self.i_cars
        self.i_cars = self.i_cars + 1
        
    def Stop(self):
        print("\nDestroying track")
        self.is_running = False
        for car in self.cars.keys():
            car.Stop()
            
    def GetNieghbbours(self, car, area=30):
        car_id = self.cars[car]
        car_loc = car.stats.location[0]
        nieghbourhood = self.track[ (car_loc-area):(car_loc+area)]
        ids = nieghbourhood[nieghbourhood!=0].ravel()
        cars = [key for key in self.cars if (self.cars[key] in ids) and self.cars[key]!=car_id ] 
        cars = np.array(cars)
        distances = [abs(car.stats.location[0] - other.stats.location[0]) for other in cars]
        cars = cars[np.argsort(distances)]
        
        return cars
        
             
    def UpdateLocations(self):
        i=0
        while(self.is_running):
            cars = list(self.cars.keys())
            for car in cars:
                car_id = self.cars[car]
                try:
                    prev_loc = np.argwhere(self.track==car_id).ravel()
                    self.track[prev_loc[0], prev_loc[1]] = 0
                except:
                    pass
                
                if(car.is_running):
                    
                    if(self.track[car.stats.location[0], car.stats.location[1]]==0):
                        self.track[car.stats.location[0], car.stats.location[1]] = car_id
                else:
                    del self.cars[car]
                    
            i=i+1
            if(i%10==0):
                print(self)
            time.sleep(0.1)
            
class Car:
    
    def __init__(self, stats, track, passive=True):
        self.stats = stats
        self.nieghbours = []
        self.track = track
        self.track.Add(self)
        self.is_running = True
        if(not passive):
            Thread(target=self.Monitor).start()
            Thread(target=self.CalulatePositionAndSpeed).start()
            
    def __str__(self):  
        _str = "<Car {}>".format(self.stats.location)
        return _str
    
    
    def Stop(self):
        self.is_running = False
        
        
    def Update(self, location, speed, acceleration):
        self.stats.location = location
        self.stats.speed = speed
        self.stats.acceleration = acceleration
        

    def CalulatePositionAndSpeed(self, step=1):  
        while(self.is_running):
            
            prev_loc = self.stats.location
            new_loc = ( int( prev_loc[0] + (self.stats.speed*step) )%self.track.track.shape[0] , prev_loc[1] )
            self.stats.location = new_loc
            self.stats.speed = self.stats.speed + (self.stats.acceleration*step)
            self.stats.speed = max (0, self.stats.speed)
            time.sleep(step)
      
        
    def Monitor(self):
        while(self.is_running):
            
            self.nieghbours = self.track.GetNieghbbours(self)
            self.ControlSpeedAndAcceleration()
            
            #print(self.stats)
            time.sleep(1)
            
    
    def SwitchLanes(self):
        self.stats.location = ( self.stats.location[0], 1-self.stats.location[1] )
            
    
    def ControlSpeedAndAcceleration(self):
        #print([str(x) for x in self.nieghbours])
        

        if(len(self.nieghbours) > 0):
            closest_car = self.nieghbours[0]
            self.stats.location = (self.stats.location[0], (1-closest_car.stats.location[1]) )
            if(self.stats.location[0] < closest_car.stats.location[0]):
                #print("Acceleration")
                self.stats.acceleration = MAX_ACCELERATION
            else:
                #print("Decceleration")
                self.stats.acceleration = MIN_ACCELERATION
        
        elif(self.stats.speed < (MAX_SPEED)):
            self.stats.acceleration = MAX_ACCELERATION
        
        elif(self.stats.speed > (MAX_SPEED)):
            self.stats.acceleration = MIN_ACCELERATION
               
            
