import sys, socket, time, threading
import logging,re,random
from opensimplex import OpenSimplex

# TESTER_PORT = 33500
delta_t=0.1#0.1s
class sensor(threading.Thread):    
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.log_file = ""
        self.node_id = ""
        self.sock = 0
        self.port = 0
        self.aodv_tester_port = 0
        self.command = ""


        self.SPEED = random.randrange(100)
        self.ACCELERATION = random.randint(-3, 6)
        self.NOISE_COUNTER_INCREMENT = 0.1# Increasing this value would mean moving faster accross perlin noise space, meaning the difference between each value would be greater.
        self.noise_counter =0
        self.STATUS = "ACTIVE"
        
    def get_tester_port(self, node_id):
        port = 33400
        return port
    
    # Return the listener port associated with the given node
    def get_aodv_tester_port(self, node_id):
        port = 33500
        return port

    def set_node_id(self, id):
        self.node_id = id
        

    # Generic routine to send the vehicle information to the protocol handler thread
    def send(self, message):
        self.sock.sendto(message, 0, ('localhost', self.aodv_tester_port))

    # TODO: broadcast the packet?
    def broadcast_packet():
        return

    def construct_packet(keys, values):
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return json.dumps(packet)

    def update(self,accelleration_change):
        if self.STATUS == "ACTIVE":
            self.ACCELERATION += accelleration_change
            self.SPEED += self.ACCELERATION

            # Some checks to make sure car isn't reversing, or is stationary for too long, etc..
            if self.SPEED < 0:
                self.SPEED = 0
            elif self.SPEED > 180:
                self.SPEED = 180
            if self.ACCELERATION < -5:
                self.ACCELERATION = -5
            elif self.ACCELERATION > 5:
                self.ACCELERATION = 5

            self.noise_counter += self.NOISE_COUNTER_INCREMENT

        # TODO: change this
        elif self.STATUS == "STOPPING":
            self.SPEED = 0;
            self.ACCELERATION =0;

        keys = ["speed", "acceleration","Ylocation","status"]
        values = [self.SPEED, self.ACCELERATION, self.YLOC,self.STATUS]

        myPacket = self.construct_packet(keys, values)
        return myPacket            

    # Default action handler
    def command_default(self):
        pass


    # Thread start routine
    def run(self):
        print("vehicle thread start")
        with open('vehicle.txt', 'w') as f:
            f.write('speed,acceleration,status\n')       
        
        noise = OpenSimplex()
        self.port = self.get_tester_port(self.node_id)
        self.aodv_tester_port = self.get_aodv_tester_port(self.node_id)
        
        # Setup socket to communicate with the AODV protocol handler thread
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))
        self.sock.setblocking(0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        
        while (True):
            # update vehicle status
            noise = OpenSimplex()
            accelleration_change = noise.noise2d(self.noise_counter, 0)
            myPacket = self.update(accelleration_change)
            sensor_type="LOCATION"
            myPacket=sensor_type+":"+myPacket
            myPacket_bytes = bytes(myPacket, 'utf-8')
            self.send(myPacket_bytes)

            # receive command from protocal handler thread
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

            with open('vehicle.txt', 'a') as f:
                f.write(str(self.SPEED)+","
                    +str(self.ACCELERATION)+","
                    +self.STATUS+"\n")

            time.sleep(0.5)

              
# End of File

