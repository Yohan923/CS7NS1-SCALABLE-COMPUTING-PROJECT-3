import threading
import time,sys,os
import numpy as np
import sys, socket, time
from threading import Timer
import logging,re,random
import config
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

TIME_INTERVAL=1
MAX_ACCELERATION = 2
MIN_ACCELERATION = -2 
MAX_SPEED = 10
TOTAL_LENGHT = 400
UPDATE_INTERVAL=1
DRAW_INTERVAL=0.1

class VehicleStatus():
    ACTIVE = 1
    INACTIVE = 0
    DARK = 20

class SpeedSensor(threading.Thread):
    
    def __init__(self,nid,loc,lane,speed,acc,status=1):
        threading.Thread.__init__(self)
        self.sock = 0
        self.port = SPEED_THREAD_PORT
        self.aodv_tester_port = 33500

        self.nid=str(nid)
        self.SPEED = speed
        self.ACCELERATION = acc
        self.LOC = loc
        self.LANE = lane
        self.DIRECTION = int(loc/100)
        if status==1:
            self.STATUS = VehicleStatus.ACTIVE
        elif status ==0:
            self.STATUS = VehicleStatus.INACTIVE

        self.neighbours={}
        temp=True
        self.visualizer=Visualizer(self.neighbours,clear= temp,table= temp, road_map=temp)
        self.visualizer.update_car_list(nid,self.constrct_dict())

        self.update_timer = 0 

        
    def send(self, message):
        message = bytes(message, 'utf-8')
        self.sock.sendto(message, 0, ('localhost', AODV_SPEED_PORT))
        self.sock.sendto(message, 0, ('localhost', SPEED_PORT))

    def broadcast_packet(self):
        return

    def construct_packet(self,keys, values):
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return json.dumps(packet)

    def constrct_dict(self):
        keys = ["speed", "location","acceleration","lane","direction"]
        values = [self.SPEED, self.LOC,self.ACCELERATION, self.LANE,self.DIRECTION]
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return packet


    def update(self):
        
        if self.STATUS == VehicleStatus.ACTIVE:
            self.ControlSpeedAndAcceleration()
            prev_loc = self.LOC
            self.LOC = int( prev_loc + (self.SPEED*TIME_INTERVAL) )%400 
            self.SPEED = self.SPEED + (self.ACCELERATION*TIME_INTERVAL)
            self.SPEED = max (0, self.SPEED)
        elif self.STATUS == VehicleStatus.INACTIVE:
            self.SPEED =0;self.ACCELERATION=0;


        keys = ["speed", "location","acceleration","lane","direction"]
        values = [self.SPEED, self.LOC,self.ACCELERATION, self.LANE,self.DIRECTION]

        self.visualizer.update_car_list(self.nid,self.constrct_dict())

        try:
            myPacket = self.construct_packet(keys, values)
            self.send(myPacket)   

            # Restart the timer
            self.update_timer.cancel()
            self.update_timer = Timer(UPDATE_INTERVAL, self.update, ())
            self.update_timer.start() 
        except:
            pass

        return 


    # Default action handler
    def command_default(self):
        pass

    def SwitchLanes(self):
        self.LANE = (self.LANE+1)%2

    def findNearest(self):
        minDis=500
        nearestNode=""
        for sender in self.neighbours.keys():
            if sender !=self.nid:
                distance = (self.neighbours[sender]['location']-self.LOC)%400
                if distance<20 and (self.LOC+distance)%400==self.neighbours[sender]['location']:
                    minDis=distance
                    nearestNode=sender
        print("nearest node: "+ str(nearestNode))
        return nearestNode

    def ControlSpeedAndAcceleration(self):
        # if(len(self.neighbours.keys())>1):
        #     # print("neighbours non empty")
        nearest=self.findNearest()
        if nearest!="": 
            closest_car = self.neighbours[nearest]
            self.LANE = 1-closest_car['lane']
            if(self.LOC < closest_car['location']):
                self.ACCELERATION= MAX_ACCELERATION
            else:
                self.ACCELERATION = MIN_ACCELERATION
        
        elif(self.SPEED < (MAX_SPEED)):
            self.ACCELERATION = MAX_ACCELERATION
            
        elif(self.SPEED > (MAX_SPEED)):
            self.ACCELERATION = MIN_ACCELERATION

    def onReceive(self,sender,msg):
        data = json.loads(msg)
        sender=str(sender)


        if sender != self.nid and self.outOfTransmissionRange(data):
            print("delete "+sender)
            self.neighbours.pop(sender)
            self.visualizer.deleteCar(sender)
            return

        if (sender in self.neighbours.keys()):
            self.neighbours[sender]['location']=data['location'];
            self.neighbours[sender]['lane'] = data['lane']; 
            self.neighbours[sender]['speed']=data['speed']; 
            self.neighbours[sender]['acceleration']=data['acceleration'];
        else:
            self.neighbours[sender] = data

        self.visualizer.update_car_list(sender,neighbours[sender])
    
    def outOfTransmissionRange(self,data):
        senderLoc = data['location']//100
        myLoc = self.LOC//100
        if abs(senderLoc - myLoc)  ==2:
            return True
        return False

    # Thread start routine
    def run(self):
        print("speed and location sensor start")      
        
        # Setup socket to communicate with the AODV protocol handler thread
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))
        self.sock.setblocking(0)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.update_timer = Timer(UPDATE_INTERVAL, self.update, ())   
        self.update_timer.start()
        self.visualizer.run()

        while (True):
            # receive
            try:
                command, _ = self.sock.recvfrom(1000)
                command = command.decode('utf-8')
                command = command.split(':', 2)
                command_type = command[0]
                self.command = command
                # print(command[0]);print(command[1]);print(command[2])

                if command_type == "RECEIVE":
                    self.onReceive(command[1],command[2])
                else:
                    self.command_default()
                time.sleep(0.01)

            except:
                pass  






class Visualizer:
    
    def __init__(self,cars,clear=True,table=True, road_map=True):
        self.cars=cars
        self.track=np.zeros((TOTAL_LENGHT, 2))
        self.road_map = road_map
        self.clear=clear
        self.table = table
        self.draw_timer=0
       
    def clear_canvas(self): 
  
        if os.name == 'nt': 
            _ = os.system('cls') 
      
        else: 
            _ = os.system('clear') 
  
    def run(self):
        if(self.clear):
            self.clear_canvas()
        
        if(self.road_map):
            self.GenerateMap()
                
        if(self.table):
            self.GenerateTable()

        self.draw_timer = Timer(DRAW_INTERVAL,  self.run,())   
        self.draw_timer.start()  
                
    def update_car_list(self,sender,car):  
        sender=str(sender)
        self.cars[sender] = car
        self.track=np.zeros((TOTAL_LENGHT, 2))
        for car_id in self.cars:
            self.track[ int(self.cars[car_id]['location']), int(self.cars[car_id]['lane'])]=int(car_id)
        # print(self.track[self.track!=0])

    def deleteCar(self,sender):
        self.cars.pop(sender)
    # def update_car_list(self,sender,new_neighbors): 
    #     self.cars = new_neighbors
    #     self.track=np.zeros((TOTAL_LENGHT, 2))
    #     for car_id in self.cars:
    #         self.track[ int(self.cars[car_id]['location']), int(self.cars[car_id]['lane'])]=int(car_id)
    #     # print(self.track[self.track!=0])


    def GenerateMap(self, sep=20):
        
        visualBuilder = ""
        visualBuilder += "\n"
        visualBuilder += ("Car Lenght: 1 meter \n")
        visualBuilder += ("Each character represents 10 meters/car lenghts. Therefore there might an overlap if cars are close to each other. \n")
        
        sep = " " * sep
        visualBuilder += "\n"
        
        
        seg = self.track[:100][:,0]
        list_00 = [" " for _ in range(10)]
        values = np.argwhere(seg!=0).ravel()
        keys = seg[values]
        for i in range(len(keys)):
            if(int(keys[i])!=0):
                list_00[9 - int(values[i]/10.)] = int(keys[i])
         
        seg = self.track[:100][:,1]
        list_01 = [" " for _ in range(10)]
        values = np.argwhere(seg!=0).ravel()
        keys = seg[values]
        for i in range(len(keys)):
            if(int(keys[i])!=0):
                list_01[9 - int(values[i]/10.)] = int(keys[i])
              
        
        
        
        seg = self.track[100:200][:,0]
        list_10 = [" " for _ in range(20)]
        values = np.argwhere(seg!=0).ravel()
        keys = seg[values]
        for i in range(len(keys)):
            if(int(keys[i])!=0):
                list_10[int(values[i]/10.)*2] = str(int(keys[i]))
         
        seg = self.track[100:200][:,1]
        list_11 = [" " for _ in range(20)]
        values = np.argwhere(seg!=0).ravel()
        keys = seg[values]
        for i in range(len(keys)):
            if(int(keys[i])!=0):
                list_11[int(values[i]/10.)*2] = str(int(keys[i]))
        
        
        
              
        
        seg = self.track[200:300][:,0]
        list_20 = [" " for _ in range(10)]
        values = np.argwhere(seg!=0).ravel()
        keys = seg[values]
        for i in range(len(keys)):
            if(int(keys[i])!=0):
                list_20[int(values[i]/10.)] = int(keys[i])
         
        seg = self.track[200:300][:,1]
        list_21 = [" " for _ in range(10)]
        values = np.argwhere(seg!=0).ravel()
        keys = seg[values]
        for i in range(len(keys)):
            if(int(keys[i])!=0):
                list_21[int(values[i]/10.)] = int(keys[i])
                
                
                
        seg = self.track[300:400][:,0]
        list_30 = [" " for _ in range(20)]
        values = np.argwhere(seg!=0).ravel()
        keys = seg[values]
        for i in range(len(keys)):
            if(int(keys[i])!=0):
                list_30[(9 - int(values[i]/10.))*2] = str(int(keys[i]))
         
        seg = self.track[300:400][:,1]
        list_31 = [" " for _ in range(20)]
        values = np.argwhere(seg!=0).ravel()
        keys = seg[values]
        for i in range(len(keys)):
            if(int(keys[i])!=0):
                list_31[(9 - int(values[i]/10.))*2] = str(int(keys[i]))


        
                
        
        visualBuilder += (sep + "-"*34 + "\n")
        visualBuilder += (sep + "|      " + "".join(list_11) + "      |" + "\n")
        visualBuilder += (sep + "|      " + "".join(list_10) + "      |" + "\n")
        visualBuilder += (sep + "|      " + "-"*20 + "      |" + "\n")
        
        for i in range(10):
            line = "|"
            cell_1_1 = list_01[i]
            cell_1_2 = list_00[i]
            cell_3_1 = list_20[i]
            cell_3_2 = list_21[i]
            line = "| {} {} |".format(cell_1_1, cell_1_2) + " "*(20) +"| {} {} |".format(cell_3_1, cell_3_2)
            visualBuilder += (sep + line) + "\n"
        
        visualBuilder += (sep + "|      " + "-"*20 + "      |" + "\n")
        visualBuilder += (sep + "|      " + "".join(list_30) + "      |" + "\n")
        visualBuilder += (sep + "|      " + "".join(list_31) + "      |" + "\n")
        visualBuilder += (sep + "-"*34) + "\n"
        print(visualBuilder)
        
        




        
    def GenerateEmptyMap(self):
        
        visualBuilder = ""
        visualBuilder += ("-"*24) + "\n"
        visualBuilder += ("|      " + " "*10 + "      |" + "\n")
        visualBuilder += ("|      " + " "*10 + "      |" + "\n")
        visualBuilder += ("|      " + "-"*10 + "      |" + "\n")
        
        for i in range(10):
            line = "|"
            cell_1_1 = " "
            cell_1_2 = " "
            cell_3_1 = " "
            cell_3_2 = " "
            line = "| {} {} |".format(cell_1_1, cell_1_2) + " "*(10) +"| {} {} |".format(cell_3_1, cell_3_2)
            visualBuilder += (line) + "\n"
        
        visualBuilder += ("|      " + "-"*10 + "      |" + "\n")
        visualBuilder += ("|      " + " "*10 + "      |" + "\n")
        visualBuilder += ("|      " + " "*10 + "      |" + "\n")
        visualBuilder += ("-"*24) + "\n"
        print(visualBuilder)
        
        
    def GenerateTable(self):
        full_vehicle_states=config.my_vehicle.get_full_vehicle_states()

        #columns = ['NODE_ID','LOCATION', 'LANE', 'SPEED (m/s)', 'ACC (m/s^2)',  'WIPER SPEED', 'LIGHT']
        columns = ['NODE_ID','X', 'Y','LANE', 'SPEED ', 'ACC ']
        columns_str = "|  " + "  |  ".join(columns) + "  |"
        columns = columns_str.split("|")[1:-1]
        sys.stdout.write("-"*len(columns_str)+"\n")
        sys.stdout.write(columns_str+"\n")
        sys.stdout.write("-"*len(columns_str)+"\n")
        
        for car_id in self.cars.keys():
            loc = int(self.cars[car_id]['location'])
            if loc//100==0:
                locx=0;locy=loc;
            elif loc//100 == 1:
                locx=loc%100;locy=100;
            elif loc//100 == 2:
                locx=100;locy=100-loc%100;
            else:
                locx=100-loc%100;locy=0;

            #loc = "{} ({})".format(loc%100, ["Left", "Top", "Right", "Bottom", "Bottom"][loc//100])
            record = [ int(car_id),
                        locx,locy,
                      ["RIGHT", "LEFT"][self.cars[car_id]['lane']],
                      self.cars[car_id]['speed'],
                      self.cars[car_id]['acceleration']
                      ]
            
            record = [str(x) for x in record]


            message = "|"
            for i in range(len(record)):
                field = record[i]
                col = columns[i]
                field_str = " "*int( (len(col)-len(field))/2 ) + field 
                field_str = field_str + ( " " *(len(col)-len(field_str)) ) +"|"
                message = message + field_str
                
            sys.stdout.write(message+"\n")
        
        sys.stdout.write("-"*len(columns_str)+"\n")
        
        visualBuilder = ""
        visualBuilder += "\n"
        if 'humidity' in full_vehicle_states.keys():
            humidity=str(full_vehicle_states['humidity'])
        else:
            humidity='/'
        if 'light_intensity' in full_vehicle_states.keys():
            light_intensity=str(full_vehicle_states['light_intensity'])
        else:
            light_intensity='/'
        visualBuilder += ("HUMIDITY: "+humidity+"\tLIGHT INTENSITY: "+light_intensity + "\n")
        visualBuilder += ("Controller Information: \n"+
            "WIPER SPEED : "+ ["STOP", "SLOW","FAST"][full_vehicle_states['wiper_speed']]+
            "\tCAR LIGHT : "+ ["OFF", "DIM","NORMAL"][full_vehicle_states['light']] + "\n")
        print(visualBuilder)





           
