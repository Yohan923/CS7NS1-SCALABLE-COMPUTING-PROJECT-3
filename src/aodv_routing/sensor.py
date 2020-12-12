import sys, socket, time, threading
import logging,re

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
        self.status = "ACTIVE"
        
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

    def update(self):
        if self.status == "ACTIVE":
            accelleration_change = noise.noise2d(noise_counter, 0)

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
            

    # Default action handler
    def command_default(self):
        pass


    # Thread start routine
    def run(self):
        print("sensor thread start")

        logging.basicConfig(level=logging.DEBUG,
                    filename='new.log',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s: %(message)s'
                    )
        
        self.port = self.get_tester_port(self.node_id)
        self.aodv_tester_port = self.get_aodv_tester_port(self.node_id)
        
        # Setup socket to communicate with the AODV protocol handler thread
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))
        self.sock.setblocking(0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        
        while (True):
            # update vehicle status
            self.update()

            # receive command from protocal handler thread
            try:
                command, _ = self.sock.recvfrom(100)
                command = command.decode('utf-8')
                command = re.split(':', command)
                print(command[0])
                command_type = command[0]
                self.command = command

                if command_type == "COMMAND_STOP":
                    print("Vehicle receive stop command ")
                    self.status = "STOP"
                else:
                    self.command_default()

            except:
                pass  


            time.sleep(1)

              
# End of File

