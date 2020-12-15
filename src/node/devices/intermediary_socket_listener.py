from threading import Thread
import socket, select

class IntermediarySocketListener(Thread):
    def __init__(
        self,
        remote_hostname,
        remote_listen_port
    ):
        Thread.__init__(self)
        self.remote_hostname = remote_hostname
        self.remote_listen_port = remote_listen_port

    def run(self):
        listener_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener_sock.bind(('localhost', self.remote_listen_port))
        listener_sock.setblocking(0)
        listener_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        inputs = [listener_sock]
        outputs = []

        print("running listener")

        while inputs:
            readable, _, _ = select.select(inputs, outputs, inputs)
            for r in readable:
                if r is listener_sock:
                    # TODO: send update from group 9 to mqtt