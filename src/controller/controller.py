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

# endregion
# endregion

print(
    "Test client sending packets to IP {0}, via port {1}\n".format(
        SERVER_IP, PORT_NUMBER
    )
)

mySocket = socket(AF_INET, SOCK_DGRAM)

while True:
    mySocket.sendto(b"cool", (SERVER_IP, PORT_NUMBER))
    time.sleep(0.5)
