from threading import Thread
import time,socket,json

PHOTO_PORT = 33885
PHOTO_THREAD_PORT = 33985
RAINFALL_PORT = 33886
RAINFALL_THREAD_PORT = 33986 
# TODO: try to proper readings
class PhotoIntensity():
    BRIGHT = 100
    DIM = 60
    DARK = 20


class PhotoSensor(Thread):
    
    def __init__(self, photo_intensity):
        Thread.__init__(self)
        self._photo_intensity = photo_intensity


    def set_photo_intensity(self, photo_intensity):
        self._photo_intensity = photo_intensity


    def get_photo_intensity(self):
        return self._photo_intensity

    def send(self, message):
        self.sock.sendto(message, 0, ('localhost', PHOTO_PORT))

    def construct_packet(self,keys, values):
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return json.dumps(packet)

    def update(self):
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
