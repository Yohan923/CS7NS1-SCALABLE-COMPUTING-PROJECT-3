from threading import Thread
import time,socket,json
HEADWAY_PORT=33882
HEADWAY_THREAD_PORT=33982

class HeadwaySensor(Thread):
    def __init__(self, distance_to_contact=100):
        Thread.__init__(self)
        self._distance_to_contact = distance_to_contact


    def set_distance_to_contact(self, distance_to_contact):
        self._distance_to_contact = distance_to_contact


    def get_distance_to_contact(self):
        return self._distance_to_contact

    def send(self, message):
        self.sock.sendto(message, 0, ('localhost', HEADWAY_PORT))

    def construct_packet(self,keys, values):
        packet = {}
        for i in range(len(keys)):
            packet[keys[i]] = values[i]
        return json.dumps(packet)

    def update(self):
        keys = ["headway"]
        values = [self._distance_to_contact]
        myPacket = self.construct_packet(keys, values)
        return myPacket



    def run(self):
        print("headway sensor start")  

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', HEADWAY_THREAD_PORT))
        self.sock.setblocking(0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        while (True):
            myPacket = self.update()
            myPacket_bytes = bytes(myPacket, 'utf-8')
            self.send(myPacket_bytes)

            with open('headway.txt', 'a') as f:
                f.write(myPacket+"\n")

            # receive
            try:
                command, _ = self.sock.recvfrom(100)
                command = command.decode('utf-8')

                # for debug purpose
                print("headway thread receive command: "+command)

            except:
                pass  

            time.sleep(60)