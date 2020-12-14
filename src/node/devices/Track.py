import numpy as np
from threading import Thread
import time

MAX_ACCELERATION = 2
MIN_ACCELERATION = -2 
MAX_SPEED = 10
TOTAL_LENGHT = 400

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
        Thread(target=self.UpdateLocations).start()
        
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
    
    def __init__(self, stats, track, passive=False):
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
            
            

# START OF THE PROGRAM
track = Track()
myself = Car( Stats( (10,0), 0, 0 ), track=track)
#car2 = Car( Stats( (5,0), 0, 0 ), track=track, passive=True)
#car3 = Car( Stats( (0,0), 0, 0 ), track=track, passive=True)

# VARIABLES TO TRASMIT
myself.stats.location
myself.stats.speed
myself.stats.acceleration


# NEW CAR JOINED
car2 = Car( Stats( (1,0), 0, 0 ), track=track, passive=True)

# CARUPDATE RECIEVED
car2.Update((300, 1), 10, 0)

# CAR CONNECTION LOST
car2.Stop()


time.sleep(30)
track.Stop()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    