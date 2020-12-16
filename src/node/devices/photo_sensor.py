from threading import Thread
import time,socket,json


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


# TODO: try to proper readings
class PhotoIntensity():
    BRIGHT = 100
    DIM = 60
    DARK = 20


class PhotoSensor(Thread):
    
    def __init__(self, photo_intensity=100):
        Thread.__init__(self)
        self._photo_intensity = int(photo_intensity)


    def set_photo_intensity(self, photo_intensity):
        self._photo_intensity = int(photo_intensity)


    def get_photo_intensity(self):
        return int(self._photo_intensity)

    def send(self, message):
        self.sock.sendto(message, 0, ('localhost', PHOTO_PORT))
        self.sock.sendto(message, 0, ('localhost', LIGHT_THREAD_PORT))
        self.sock.sendto(message, 0, ('localhost', AODV_SPEED_PORT))

    def construct_packet(self,keys, values):
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return json.dumps(packet)

    def update(self):
        self._photo_intensity-=5
        if self._photo_intensity<1:
            self._photo_intensity=1
        keys = ["light_intensity"]
        values = [self._photo_intensity]
        myPacket = self.construct_packet(keys, values)
        return myPacket

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', PHOTO_THREAD_PORT))
        self.sock.setblocking(0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        while (True):
            myPacket = self.update()
            myPacket_bytes = bytes(myPacket, 'utf-8')
            self.send(myPacket_bytes)

            with open('photo_sensor.txt', 'a') as f:
                f.write(myPacket+"\n")

            # receive
            try:
                command, _ = self.sock.recvfrom(100)
                command = command.decode('utf-8')


            except:
                pass  

            time.sleep(5)
