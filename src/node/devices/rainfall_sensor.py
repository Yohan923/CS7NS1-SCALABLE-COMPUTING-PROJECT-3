from threading import Thread
import time,socket,json
PHOTO_PORT = 33885
PHOTO_THREAD_PORT = 33985
RAINFALL_PORT = 33886
RAINFALL_THREAD_PORT = 33986 

# rainfall measured by the critical angle between the glass and infrared, the critical angle for total internal refraction is around 42°
# when glass is dry, 60° when wet, assume 70° for very wet
class RainfallLevel():
    HIGH = 70
    MILD = 60
    DRY = 42


class RainfallSensor(Thread):
    
    def __init__(self, rainfall):
        Thread.__init__(self)
        self._rainfall = rainfall


    def set_rainfall(self, rainfall):
        self._rainfall = rainfall


    def get_rainfall(self):
        return self._rainfall

    def send(self, message):
        self.sock.sendto(message, 0, ('localhost', RAINFALL_PORT))

    def construct_packet(self,keys, values):
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return json.dumps(packet)

    def update(self):
        keys = ["humidity"]
        values = [self._distance_to_contact]
        myPacket = self.construct_packet(keys, values)
        return myPacket

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', RAINFALL_THREAD_PORT))
        self.sock.setblocking(0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        while (True):
            myPacket = self.update()
            myPacket_bytes = bytes(myPacket, 'utf-8')
            self.send(myPacket_bytes)

            with open('rainfall_sensor.txt', 'a') as f:
                f.write(myPacket+"\n")

            # receive
            try:
                command, _ = self.sock.recvfrom(100)
                command = command.decode('utf-8')

                # for debug purpose
                print("rainfall thread receive command: "+command)

            except:
                pass  

            time.sleep(5)