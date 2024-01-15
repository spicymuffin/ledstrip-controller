import random
from rpi_ws281x import *


def getRandomColor():
    return Color(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def getRandomRGBColor(_w):
    return Color(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        _w,
    )


"""
w channel defaults to 0
"""


def decode_color(_input):
    try:
        if _input == "rnd":
            return getRandomColor()
        elif _input == "rndrgb":
            splt = _input.split(";")
            return getRandomRGBColor(int(splt[1]))
        else:
            splt = _input.split(";")
            return Color(*list(map(int, splt)))
    except:
        return -1


def parse_list(_input):
    try:
        return _input.split("|")
    except:
        return -1


if __name__ == "__main__":
    print()
