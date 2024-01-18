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


ANIM_DICT = {
    "colorwipesequence": {
        "class": animation_colorwipesequence,
        "aliases": ["colorwipesequence", "cws"],
    },
    "colorwiperandom": {
        "class": animation_colorwiperandom,
        "aliases": ["colorwiperandom", "cwr"],
    },
    "off": {
        "class": animation_off,
        "aliases": ["off"],
    },
    "theaterchase": {
        "class": animation_theaterchase,
        "aliases": ["theaterchase", "tc"],
    },
    "theaterchaserainbow": {
        "class": animation_theaterchaserainbow,
        "aliases": ["theaterchaserainbow, tcr"],
    },
    "rainbowcycle": {
        "class": animation_rainbowcycle,
        "aliases": ["rainbowcycle", "rbc", "rc"],
    },
    "cancer": {
        "class": animation_cancer,
        "aliases": ["cancer", "cncr"],
    },
}


def animationcode_interpret(_animation_code):
    global ANIM_DICT

    for i in ANIM_DICT.keys():
        if _animation_code in ANIM_DICT[i]["aliases"]:
            return i
    return -1


def chunkdata_interpret(_chunk_data):
    try:
        comma_splt = _chunk_data.split(",")
        l = list(map(int, comma_splt))
        print(l)
    except:
        return -1
    return l


def command_change_animation(_args):
    global ANIM_DICT
    global STRIP

    if len(_args) < 2:
        return (-1, "chunk_data/animation_code fault")

    ac = _args[0]
    chunk_data = _args[1]
    args = _args[2:]

    ac_interpret_result = animationcode_interpret(_animation_code=ac)

    if ac_interpret_result == -1:
        return (-1, "animationcode interpretation fault")

    anim = ANIM_DICT[ac_interpret_result]["class"]
    chunk_data_interpret_result = chunkdata_interpret(_chunk_data=chunk_data)

    set_animation_result = None

    try:
        for a in chunk_data_interpret_result:
            set_animation_result = STRIP.chunks[a].set_animation(anim, args)
    except:
        return (-1, "chunk setting error")  # probably never going to trigger but eh

    if set_animation_result[0] == -1:
        return (-1, set_animation_result[1])

    return (0, "ack")


def command_ping(_args):
    return (0, "data")


def command_off(_args):
    global STRIP

    return command_change_animation(
        ["off", ",".join(list(map(str, range(len(STRIP.chunks)))))]
    )


def command_make_chunk(_args):
    if len(_args) < 2:
        return (-1, "chunk boundaries setting error")

    s = _args[0]
    e = _args[1]

    try:
        s = int(s)
        e = int(e)
    except:
        return (-1, "invalid boundaries")


CMD_MAP = {
    "off": command_off,
    "change_animation": command_change_animation,
    "ping": command_ping,
    "make_chunk": command_make_chunk,
}


def payload_executor(payload):
    splt = payload.split()
    cmd = splt[0]
    args = splt[1:]

    return CMD_MAP[cmd](args)


def listen():
    global RECV_SOCKET
    global STRIP
    global EXECUTION_THREAD

    while True:
        (data, addr) = RECV_SOCKET.recvfrom(SIZE)
        print(data, addr)
        decoded = data.decode()
        result = payload_executor(payload=decoded)
        RECV_SOCKET.sendto(result[1].encode("utf-8"), addr)


if __name__ == "__main__":
    startup()
    listen()
