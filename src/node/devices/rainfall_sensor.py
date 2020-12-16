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

# rainfall measured by the critical angle between the glass and infrared, the critical angle for total internal refraction is around 42°
# when glass is dry, 60° when wet, assume 70° for very wet
class RainfallLevel():
    HIGH = 70
    MILD = 60
    DRY = 42


class RainfallSensor(Thread):
    
    def __init__(self, rainfall=42):
        Thread.__init__(self)
        self._rainfall = int(rainfall)


    def set_rainfall(self, rainfall):
        self._rainfall = int(rainfall)


    def get_rainfall(self):
        return int(self._rainfall)

    def send(self, message):
        self.sock.sendto(message, 0, ('localhost', RAINFALL_PORT))
        self.sock.sendto(message, 0, ('localhost', WIPER_THREAD_PORT))
        self.sock.sendto(message, 0, ('localhost', AODV_SPEED_PORT))

    def construct_packet(self,keys, values):
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return json.dumps(packet)

    def update(self):
        self._rainfall+=5
        if self._rainfall>100:
            self._rainfall=100     
        keys = ["humidity"]
        values = [self._rainfall]
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