
from network.connection import Network

def join_game(host_ip):
    n = Network(host_ip, 5555)
    return n
    