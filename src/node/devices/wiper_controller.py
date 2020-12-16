from node.devices.rainfall_sensor import RainfallLevel
from threading import Thread
import time,socket,json,re

WIPER_PORT=33883
WIPER_THREAD_PORT=33983

class WIPER_SPEED():
    FAST = 2
    SLOW = 1
    STOP = 0

class WiperController(Thread):

    def __init__(self, wiper_speed):
        Thread.__init__(self)
        self._wiper_speed = wiper_speed

    
    def set_speed(self, wiper_speed):
        self._wiper_speed = wiper_speed

    
    def get_speed(self):
        return self._wiper_speed
    

    # rainfall measured by the critical angle between the glass and infrared, the critical angle for total internal refraction is around 42°
    # when glass is dry, 60° when wet, assume 70° for very wet
    def set_speed_by_rainfall(self, rainfall):
        print(rainfall)
        if rainfall <= RainfallLevel.DRY:
            self.set_speed(WIPER_SPEED.STOP)
        elif rainfall <= RainfallLevel.MILD:
            self.set_speed(WIPER_SPEED.SLOW)
        else:
            self.set_speed(WIPER_SPEED.FAST)
        print("set wiper speed to "+["STOP","SLOW","FAST"][self.get_speed()])

    def send(self, message):
        self.sock.sendto(message, 0, ('localhost', WIPER_PORT))

    def construct_packet(self,keys, values):
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return json.dumps(packet)

    def update(self):
        keys = ["wiper_speed"]
        values = [self.get_speed()]
        myPacket = self.construct_packet(keys, values)
        return myPacket


    def run(self):
        print("wiper controller start")  

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', WIPER_THREAD_PORT))
        self.sock.setblocking(0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        while (True):
            myPacket = self.update()
            myPacket_bytes = bytes(myPacket, 'utf-8')
            self.send(myPacket_bytes)

            with open('wiper.txt', 'a') as f:
                f.write(myPacket+"\n")

            # receive
            try:
                # command, _ = self.sock.recvfrom(100)
                # command = command.decode('utf-8')
                # command = re.split('\'',command)
                # message = {}
                # message[command[1]]=int(command[3])    
                command, _ = self.sock.recvfrom(100)
                command = command.decode('utf-8')
                commands = re.split('\'',command)
                message = {}
                temp=commands[2]
                message[commands[1]]=int(temp[2:-2])                        
                if 'humidity' in message.keys():
                    self.set_speed_by_rainfall( message['humidity'])



            except:
                pass  

            time.sleep(3)
