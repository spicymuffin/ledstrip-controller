# library imports
from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM
import sys

# custom imports
import ledcontroller

# region global vars
# region runopt
PORT_NUMBER = 5000
SIZE = 1024
# endregion
# region runtime
RECV_SOCKET = None
# endregion
# endregion


def startup():
    global PORT_NUMBER
    global SIZE
    global RECV_SOCKET

    hostname = gethostbyname("0.0.0.0")

    RECV_SOCKET = socket(AF_INET, SOCK_DGRAM)
    RECV_SOCKET.bind((hostname, PORT_NUMBER))

    print(f"Test server listening on port {PORT_NUMBER}.")


def listen():
    global RECV_SOCKET
    while True:
        (data, addr) = RECV_SOCKET.recvfrom(SIZE)
        print(data, addr)


if __name__ == "main":
    startup()
