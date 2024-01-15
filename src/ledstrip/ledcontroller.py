import time
import threading

import util

from rpi_ws281x import *

# region LED strip configuration:
LED_COUNT = 240  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
LED_STRIP = ws.SK6812_STRIP_RGBW
# endregion


class ledstrip:
    def __init__(self) -> None:
        self.neopixel = self.initialize_strip()
        self.chunks = [chunk(0, LED_COUNT - 1, self.neopixel)]

    def start_mainloop(self):
        pass

    def initialize_strip(self):
        # Create NeoPixel object with appropriate configuration.
        strip = Adafruit_NeoPixel(
            LED_COUNT,
            LED_PIN,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL,
            LED_STRIP,
        )
        # Intialize the library (must be called once before other functions).
        strip.begin()
        return strip


class chunk:
    def __init__(self, _start, _end, _neopixel) -> None:
        self.start = _start
        self.end = _end
        self.num_pixels = _start - _end + 1
        self.neopixel = _neopixel
        self.animation = animation_colorwiperandom(self, "idc", 0)
        self.animation.start()

    def set_animation(self, _animation_class, _anim_args):
        self.animation.stop()
        sanitation_result = None
        try:
            sanitation_result = _animation_class.sanitize_arguments(*_anim_args)
        except Exception as ex:
            return (-1, f"sanitator pass fault {ex}")

        if sanitation_result[0] == -1:
            return (-1, f"sanitation error: {sanitation_result[1]}")
        self.animation = _animation_class(self, *(sanitation_result[1]))
        print(self.animation)
        self.animation.start()
        return (0, "animation set")

    def __str__(self) -> str:
        return f"chunk: start={self.start}; end={self.end}"


# region animations


class animation:
    def __init__(self, _chunk) -> None:
        self.chunk = _chunk
        self.stopflag = False
        self.animation_thread = None
        self.strip = self.chunk.neopixel

    def stop(self):
        self.stopflag = True
        self.animation_thread.join()
        self.stopflag = False

    def start(self):
        self.animation_thread = threading.Thread(target=self.exec, args=())
        self.animation_thread.daemon = True
        self.animation_thread.start()

    def exec(self):
        while True:
            if self.stopflag:
                break
            else:
                print("undefined animation!")


class animation_colorwiperandom(animation):
    def __init__(self, _chunk, _w, _wait_ms) -> None:
        super().__init__(_chunk)
        self.w = _w
        self.wait_ms = _wait_ms

    def exec(self):
        while True:
            if type(self.w) == int:
                self.color = util.getRandomRGBColor(self.w)
            else:
                self.color = util.getRandomColor()
            if self.stopflag:
                return
            for i in range(self.chunk.start, self.chunk.end + 1):
                if self.stopflag:
                    return
                self.strip.setPixelColor(i, self.color)
                self.strip.show()
                time.sleep(self.wait_ms / 1000.0)

    @staticmethod
    def sanitize_arguments(_w, _wait_ms):
        w = None
        wait_ms = None

        try:
            w = int(_w)
        except:
            return (-1, "invalid w")
        try:
            wait_ms = int(_wait_ms)
        except:
            return (-1, "invalid wait_ms")

        return (0, (w, wait_ms))


class animation_colorwipesequence(animation):
    def __init__(self, _chunk, _colors, _wait_ms) -> None:
        super().__init__(_chunk)
        self.colors = _colors
        self.wait_ms = _wait_ms

    def exec(self):
        self.i = 0
        while True:
            self.color = self.colors[i % len(self.colors)]
            if self.stopflag:
                return
            for i in range(self.chunk.start, self.chunk.end + 1):
                if self.stopflag:
                    return
                self.strip.setPixelColor(i, self.color)
                self.strip.show()
                time.sleep(self.wait_ms / 1000.0)

    @staticmethod
    def sanitize_arguments(_colors, _wait_ms):
        colors = []
        wait_ms = None

        try:
            tmp = util.parse_list(_colors)
            for c in tmp:
                colors.append(util.decode_color(c))
        except:
            return (-1, "invalid colors")
        try:
            wait_ms = int(_wait_ms)
        except:
            return (-1, "invalid wait_ms")

        return (0, (colors, wait_ms))


class animation_off(animation):
    def __init__(self, _chunk) -> None:
        animation.__init__(self, _chunk)

    def exec(self):
        off_color = Color(0, 0, 0, 0)
        for i in range(self.chunk.start, self.chunk.end + 1):
            self.strip.setPixelColor(i, off_color)
        self.strip.show()

    @staticmethod
    def sanitize_arguments():
        return (0, ())


class animation_cancer(animation):
    def __init__(self, _chunk, _wait_ms) -> None:
        animation.__init__(self, _chunk)
        self.wait_ms = _wait_ms

    def exec(self):
        while True:
            if self.stopflag:
                return
            for i in range(self.chunk.start, self.chunk.end + 1):
                if self.stopflag:
                    return
                self.strip.setPixelColor(i, util.getRandomRGBColor(0))
            self.strip.show()
            time.sleep(self.wait_ms / 1000.0)

    @staticmethod
    def sanitize_arguments(_wait_ms):
        wait_ms = None
        try:
            wait_ms = int(_wait_ms)
        except:
            return (-1, "invalid wait_ms")
        return (0, (wait_ms,))


class animation_theaterchase(animation):
    def __init__(self, _chunk, _color, _wait_ms) -> None:
        super().__init__(_chunk)
        self.color = _color
        self.wait_ms = _wait_ms

    def exec(self):
        while True:
            if self.stopflag:
                return
            for q in range(3):
                for i in range(self.chunk.start, self.chunk.end + 1, 3):
                    self.strip.setPixelColor(i + q, self.color)
                self.strip.show()
                time.sleep(self.wait_ms / 1000.0)
                for i in range(self.chunk.start, self.chunk.end + 1, 3):
                    self.strip.setPixelColor(i + q, 0)

    @staticmethod
    def sanitize_arguments(_color, _wait_ms):
        color = None
        wait_ms = None

        color = util.decode_color(_color)

        if color == -1:
            return (-1, "invalid color")

        try:
            wait_ms = int(_wait_ms)
        except:
            return (-1, "invalid wait_ms")

        return (0, (color, wait_ms))


class animation_theaterchaserainbow(animation):
    def __init__(self, _chunk, _wait_ms=50) -> None:
        super().__init__(_chunk)
        self.wait_ms = _wait_ms

    def exec(self):
        while True:
            if self.stopflag:
                return
            for j in range(256):
                for q in range(3):
                    for i in range(self.chunk.start, self.chunk.end + 1, 3):
                        self.strip.setPixelColor(i + q, util.wheel((i + j) % 255))
                    self.strip.show()
                    time.sleep(self.wait_ms / 1000.0)
                    for i in range(self.chunk.start, self.chunk.end + 1, 3):
                        self.strip.setPixelColor(i + q, 0)

    @staticmethod
    def sanitize_arguments(_wait_ms):
        wait_ms = None
        try:
            wait_ms = int(_wait_ms)
        except:
            return (-1, "invalid wait_ms")
        return (0, (wait_ms,))


class animation_rainbowcycle(animation):
    def __init__(self, _chunk, _wait_ms=100) -> None:
        super().__init__(_chunk)
        self.wait_ms = _wait_ms

    def exec(self):
        while True:
            if self.stopflag:
                return
            for j in range(256):
                for i in range(self.chunk.start, self.chunk.end + 1):
                    self.strip.setPixelColor(
                        i, util.wheel(((i * 256 // self.chunk.num_pixels) + j) & 255)
                    )
                self.strip.show()
                time.sleep(self.wait_ms / 1000.0)

    @staticmethod
    def sanitize_arguments(_wait_ms):
        wait_ms = None
        try:
            wait_ms = int(_wait_ms)
        except:
            return (-1, "invalid wait_ms")
        return (0, (wait_ms,))


# endregion


def rainbow(strip, wait_ms=100 & 255):
    strip.show()
    time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=200, iterations=500000):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(
                i, util.wheel(((i * 256 // strip.numPixels()) + j) & 255)
            )
        strip.show()
        time.sleep(wait_ms / 1000.0)


if __name__ == "__main__":
    strip = ledstrip()
    i = 0
    while True:
        time.sleep(1)
        i += 1
        print(f"animating... {strip.chunks[0]}")
        if i == 5:
            strip.chunks[0].set_animation(animation_rainbowcycle(strip.chunks[0]))
