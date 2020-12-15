from threading import Thread

class IntermediarySocketWriter(Thread):
    def __init__(
        self,
        remote_hostname,
        remote_send_port
    ):
        Thread.__init__(self)
        self.remote_hostname=remote_hostname
        self.remote_send_port=remote_send_port

        self.g9_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.g9_sock.bind(('', self.aodv_port))
        self.g9_sock.setblocking(0)
        self.g9_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def msg_send(self, destination, destination_port, message):
        try:
            message_bytes = bytes(message, 'utf-8')
            destination_ip = self.get_aodv_ip(destination)
            self.g9_sock.sendto(message_bytes, 0, 
                                  (destination_ip, destination_port))
        except:
            pass    
