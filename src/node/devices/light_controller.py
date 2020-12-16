from node.devices.photo_sensor import PhotoIntensity
import time,socket,json,re
from threading import Thread

LIGHT_PORT=33884
LIGHT_THREAD_PORT=33984

class LIGHT_INTENSITY():
    OFF = 0
    DIM = 1
    NORMAL = 2

class LightController(Thread):

    def __init__(self, headlight_state):
        Thread.__init__(self)
        self._headlight_state = headlight_state

    
    def set_state(self, headlight_state):
        self._headlight_state = headlight_state
    
    def get_state(self):
        return self._headlight_state
    
    
    def set_speed_by_photo_intensity(self, photo_intensity):
        print(photo_intensity)
        if photo_intensity >= PhotoIntensity.BRIGHT:
            self.set_state(LIGHT_INTENSITY.OFF)
        elif photo_intensity <= PhotoIntensity.DARK:
            self.set_state(LIGHT_INTENSITY.NORMAL)
        else:
            self.set_state(LIGHT_INTENSITY.DIM)

    def send(self, message):
        self.sock.sendto(message, 0, ('localhost', LIGHT_PORT))

    def construct_packet(self,keys, values):
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return json.dumps(packet)

    def update(self):
        keys = ["light"]
        values = [self.get_state()]
        myPacket = self.construct_packet(keys, values)
        return myPacket
 


    def run(self):
        print("light controller start")  

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', LIGHT_THREAD_PORT))
        self.sock.setblocking(0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        while (True):
            myPacket = self.update()
            myPacket_bytes = bytes(myPacket, 'utf-8')
            self.send(myPacket_bytes)

            with open('light_controller.txt', 'a') as f:
                f.write(myPacket+"\n")

            # receive
            try:
                command, _ = self.sock.recvfrom(100)
                command = command.decode('utf-8')
                commands = re.split('\'',command)
                message = {}
                temp=commands[2]
                message[commands[1]]=int(temp[2:-2])
                if 'light_intensity' in message.keys():
                    self.set_speed_by_photo_intensity(message['light_intensity'])

            except:
                pass  
            time.sleep(3)
