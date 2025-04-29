import socket
import pickle

class Network:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = host
        self.port = port
        self.addr = (self.server, self.port)
        self.client.connect(self.addr)
        self.client.setblocking(False)

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
        except socket.error as e:
            print("Send error:", e)

    def receive(self):
        try:
            packet = self.client.recv(4096)
            if packet:
                return pickle.loads(packet)
        except BlockingIOError:
            # no data ready
            return None
        except socket.error as e:
            print("Receive error:", e)
            return None
        return None
