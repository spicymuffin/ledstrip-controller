# WakaTime:
# https://www.google.com/search?q=wakatime&oq=wakatim&gs_lcrp=EgZjaHJvbWUqDQgAEAAYgwEYsQMYgAQyDQgAEAAYgwEYsQMYgAQyBggBEEUYOTIHCAIQABiABDIHCAMQABiABDIHCAQQABiABDIHCAUQABiABDIHCAYQABiABDIHCAcQABiABDIHCAgQABiABDIHCAkQABiABKgCALACAA&sourceid=chrome&ie=UTF-8
#
# manage time bruh


# library imports
from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM
import sys
import threading

# custom imports
from ledcontroller import *

# region global vars
# region runopt
PORT_NUMBER = 5000
SIZE = 1024
# endregion
# region runtime
RECV_SOCKET = None
STRIP = None
EXECUTION_THREAD = None
# endregion
# endregion


def startup():
    global PORT_NUMBER
    global SIZE
    global RECV_SOCKET
    global STRIP

    hostname = gethostbyname("0.0.0.0")

    RECV_SOCKET = socket(AF_INET, SOCK_DGRAM)
    RECV_SOCKET.bind((hostname, PORT_NUMBER))

    print(f"server listening on port {PORT_NUMBER}.")

    STRIP = ledstrip()
    i = 0
    STRIP.chunks[0].set_animation(animation_rainbowcycle(STRIP.chunks[0]))


def listen():
    global RECV_SOCKET
    global STRIP
    global EXECUTION_THREAD

    while True:
        (data, addr) = RECV_SOCKET.recvfrom(SIZE)
        print(data, addr)
        decoded = data.decode()


if __name__ == "__main__":
    startup()
    listen()
