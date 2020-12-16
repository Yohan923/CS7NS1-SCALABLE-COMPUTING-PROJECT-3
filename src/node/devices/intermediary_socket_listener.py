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
        self.listener_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_sock.bind(('0.0.0.0', self.remote_listen_port))
        self.listener_sock.listen(10)
        self.listener_sock.setblocking(0)
        self.listener_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        inputs = [self.listener_sock]
        outputs = []


        while inputs:
            readable, _, _ = select.select(inputs, outputs, inputs)
            for r in readable:
                if r is self.listener_sock:
                    connection, client_address = r.accept()
                    message, _ = connection.recvfrom(200)

                    # Process message and push to mqtt
                    # Example:
                    #   b'{"id": 3, "speed": 69, "brightness": 54662, "fuel": 51.05269686379842}'
                    print(message)