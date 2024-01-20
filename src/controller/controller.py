# library imports
import sys
import os
from socket import socket, AF_INET, SOCK_DGRAM
import time

# region global vars
# region runopt
SERVER_IP = "192.168.137.22"
PORT_NUMBER = 5000
SIZE = 1024
SCRIPTS_SUBFOLDER_NAME = "scripts"
# endregion
# region runtime
SEND_SOCKET = None
CURR_PATH = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_SUBFOLDER_PATH = CURR_PATH + "\\" + SCRIPTS_SUBFOLDER_NAME
# endregion
# endregion


def startup():
    global SEND_SOCKET
    SEND_SOCKET = socket(AF_INET, SOCK_DGRAM)
    mainloop()


def executor_load(args):
    global SEND_SOCKET

    args = args[0]

    lines = None
    try:
        f = open(SCRIPTS_SUBFOLDER_PATH + "\\" + args)
        lines = f.readlines()
        f.close()
    except Exception as ex:
        print(f"error opening file: {ex}")
        return

    for line in lines:
        cmd, payload = interpret(line[:-1])
        SEND_SOCKET.sendto(payload.encode("utf-8"), (SERVER_IP, PORT_NUMBER))
        data, (ip, port) = SEND_SOCKET.recvfrom(1024)
        print(data)


LOCAL_CMDS = {"load": executor_load}


def mainloop():
    global SEND_SOCKET
    global LOCAL_CMDS

    while True:
        inp = input()
        cmd, payload = interpret(inp)
        if payload == -1:
            print(f"'{cmd}' command unrecognized....")
        elif cmd in LOCAL_CMDS.keys():
            LOCAL_CMDS[cmd](payload)
        else:
            SEND_SOCKET.sendto(payload.encode("utf-8"), (SERVER_IP, PORT_NUMBER))
            data, (ip, port) = SEND_SOCKET.recvfrom(1024)
            print(data)


def plgenerator_change_animation(args):
    return "change_animation" + (" " + " ".join(args)) if len(args) != 0 else ""


def plgenerator_ping(args):
    return "ping" + (" " + " ".join(args)) if len(args) != 0 else ""


def plgenerator_off(args):
    return "off"


def plgenerator_make_chunk(args):
    return "make_chunk" + (" " + " ".join(args)) if len(args) != 0 else ""


def plgenerator_load(args):
    return args


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
    "load": {
        "plgenerator": plgenerator_load,
        "aliases": [
            "load",
            "l",
        ],
    },
    "make_chunk": {
        "plgenerator": plgenerator_make_chunk,
        "aliases": [
            "make_chunk",
            "makechunk",
            "mc",
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
