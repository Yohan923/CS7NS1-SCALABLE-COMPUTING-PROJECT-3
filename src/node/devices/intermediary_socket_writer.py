from threading import Thread
import socket

class IntermediarySocketWriter():
    def __init__(
        self,
        remote_hostname,
        remote_send_port
    ):
        self.remote_hostname=remote_hostname
        self.remote_send_port=remote_send_port
        print(self.remote_hostname)
        print(self.remote_send_port)

        self.g9_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.g9_sock.bind(('', self.remote_send_port))
        self.g9_sock.setblocking(0)
        self.g9_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def msg_send(self, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((self.remote_hostname, self.remote_send_port))
                except ConnectionResetError as e:
                    print(e)
                    return
                s.send(message)

        except:
            pass
