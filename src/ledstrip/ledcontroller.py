import random
import time
import threading

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


# region helper
def getRandomColor():
    return Color(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


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
        self.animation = animation_colorwipe(self)
        self.animation.start()

    def set_animation(self, _animation):
        self.animation.stop()
        self.animation = _animation
        self.animation.start()

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


class animation_colorwipe(animation):
    def __init__(self, _chunk, _color=getRandomColor(), _wait_ms=0) -> None:
        super().__init__(_chunk)
        self.color = _color
        self.wait_ms = _wait_ms

    def exec(self):
        while True:
            self.color = getRandomColor()
            if self.stopflag:
                return
            for i in range(self.chunk.start, self.chunk.end + 1):
                if self.stopflag:
                    return
                self.strip.setPixelColor(i, self.color)
                self.strip.show()
                time.sleep(self.wait_ms / 1000.0)


class animation_off(animation):
    def __init__(self, _chunk) -> None:
        animation.__init__(self, _chunk)

    def exec(self):
        off_color = Color(0, 0, 0, 0)
        for i in range(self.chunk.start, self.chunk.end + 1):
            self.strip.setPixelColor(i, off_color)
        self.strip.show()


class animation_theaterchase(animation):
    def __init__(self, _chunk, _color=getRandomColor(), _wait_ms=50) -> None:
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
                        self.strip.setPixelColor(i + q, wheel((i + j) % 255))
                    self.strip.show()
                    time.sleep(self.wait_ms / 1000.0)
                    for i in range(self.chunk.start, self.chunk.end + 1, 3):
                        self.strip.setPixelColor(i + q, 0)


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
                        i, wheel(((i * 256 // self.chunk.num_pixels) + j) & 255)
                    )
                self.strip.show()
                time.sleep(self.wait_ms / 1000.0)


# endregion


def rainbow(strip, wait_ms=100 & 255):
    strip.show()
    time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=200, iterations=500000):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(((i * 256 // strip.numPixels()) + j) & 255))
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
            strip.chunks[0].set_animation(
                animation_rainbowcycle(strip.chunks[0])
            )
