# library imports
import sys
from socket import socket, AF_INET, SOCK_DGRAM
import time

# region global vars
# region runopt
SERVER_IP = "192.168.137.176"
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
    SEND_SOCKET.settimeout(1)
    print("lia-ledstrip-controller ver. 0.5")
    mainloop()


def mainloop():
    global SEND_SOCKET
    while True:
        inp = input()
        cmd, payload = interpret(inp)
        if payload == -1:
            print(f"'{cmd}' command unrecognized....")
        else:
            SEND_SOCKET.sendto(payload.encode("utf-8"), (SERVER_IP, PORT_NUMBER))
            data, (ip, port) = SEND_SOCKET.recvfrom(1024)
            print(data)


def plgenerator_change_animation(args):
    return "change_animation" + (" " + " ".join(args)) if len(args) != 0 else ""


def plgenerator_ping(args):
    pass


def plgenerator_off():
    return "off"


command_dictionary = {
    "change_animation": {
        "plgenerator": plgenerator_change_animation,
        "aliases": [
            "change_animation",
            "changeanimation",
            "change_anim",
            "changeanim",
            "ca",
        ],
    },
    "ping": {
        "plgenerator": plgenerator_ping,
        "aliases": [
            "ping",
            "p",
        ],
    },
    "off": {
        "plgenerator": plgenerator_off,
        "aliases": [
            "off",
            "o",
        ],
    },
}


def cmd_argument_interpreter(command_argument):
    global command_dictionary

    for i in command_dictionary.keys():
        if command_argument in command_dictionary[i]["aliases"]:
            return i
    return -1


def interpret(input):
    splt = input.split()
    cmd = splt[0]
    args = splt[1:]

    cmd_intepret_result = cmd_argument_interpreter(command_argument=cmd)

    if cmd_intepret_result == -1:
        return (cmd, -1)

    # generate payload
    payload = command_dictionary[cmd_intepret_result]["plgenerator"](args)

    return (cmd, payload)


if __name__ == "__main__":
    startup()
