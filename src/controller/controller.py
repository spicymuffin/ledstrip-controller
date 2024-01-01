# library imports
import sys
from socket import socket, AF_INET, SOCK_DGRAM
import time

# region global vars
# region runopt
SERVER_IP = "192.168.137.22"
PORT_NUMBER = 5000
SIZE = 1024
# endregion
# region runtime
SEND_SOCKET = None
# endregion
# endregion


def startup():
    global SEND_SOCKET
    SEND_SOCKET = socket(AF_INET, SOCK_DGRAM)


def mainloop():
    global SEND_SOCKET
    while True:
        SEND_SOCKET.sendto(b"cool", (SERVER_IP, PORT_NUMBER))
        time.sleep(0.5)


if __name__ == "main":
    startup()
    mainloop()
