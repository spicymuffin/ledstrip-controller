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
        self.chunks = [
            chunk(0, LED_COUNT // 2 - 1, self.neopixel),
            chunk(LED_COUNT // 2, LED_COUNT - 1, self.neopixel),
        ]
        self.tick = 0

    def update(self):
        upd = False
        for i in range(len(self.chunks)):
            animref = self.chunks[i].animation
            if self.tick % animref.update_rate == 0:
                animref.update(self.tick)
                upd = True
        if upd:
            self.neopixel.show()
        self.tick += 1

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

    def make_chunk(self, _start, _end):
        i = 0
        insert_flag = False
        while i < len(self.chunks):
            if self.chunks[i].end < _start:
                i += 1
                continue
            if _end < self.chunks[i].start:
                i += 1
                continue

            if _start <= self.chunks[i].start <= _end:
                self.chunks[i].start = _end + 1
                if self.chunks[i].start > self.chunks[i].end:
                    self.chunks[i].animation.stop()
                    self.chunks.pop(i)
                    i -= 1
                if not insert_flag:
                    self.chunks.insert(i, chunk(_start, _end, self.neopixel))
                    insert_flag = True
            elif _start <= self.chunks[i].end <= _end:
                self.chunks[i].end = _start - 1
                if self.chunks[i].start > self.chunks[i].end:
                    self.chunks[i].animation.stop()
                    self.chunks.pop(i)
                    i -= 1
                if not insert_flag:
                    self.chunks.insert(i, chunk(_start, _end, self.neopixel))
                    insert_flag = True
            elif _start <= self.chunks[i].start and self.chunks[i].end <= _end:
                self.chunks[i].animation.stop()
                self.chunks.pop(i)
                i -= 1
            elif self.chunks[i].start < _start and _end < self.chunks[i].end:
                c_s = self.chunks[i].start
                c_e = self.chunks[i].end
                self.chunks[i].animation.stop()
                self.chunks.pop(i)
                self.chunks.insert(i, chunk(_end + 1, c_e, self.neopixel))
                self.chunks.insert(i, chunk(_start, _end, self.neopixel))
                self.chunks.insert(i, chunk(c_s, _start - 1, self.neopixel))
                return
            i += 1
        print("inserted chunk")

    def print_chunk_segmentation(self):
        global LED_COUNT
        i = 0
        print(len(self.chunks))
        for i in range(len(self.chunks)):
            for _ in range(self.chunks[i].num_pixels):
                print(i, end="")
        print()


class chunk:
    def __init__(self, s, e, _neopixel) -> None:
        self._start = s
        self._end = e
        self.num_pixels = self.calculate_num_pixels()
        self.neopixel = _neopixel
        self.animation = animation_colorwiperandom(self, 3, "idc")
        self.animation.start()

    def calculate_num_pixels(self):
        return self._end - self._start + 1

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @start.setter
    def start(self, s):
        self._start = s
        self.num_pixels = self.calculate_num_pixels()

    @end.setter
    def end(self, e):
        self._end = e
        self.num_pixels = self.calculate_num_pixels()

    def set_animation(self, _animation_class, _default_update_rate, _anim_args):
        self.animation.stop()
        sanitation_result = None
        default_sanitation_result = None

        try:
            default_sanitation_result = animation.sanitize_default_arguments(
                _default_update_rate
            )
            sanitation_result = _animation_class.sanitize_arguments(*_anim_args)
        except Exception as ex:
            return (-1, f"sanitator pass fault {ex}")

        if default_sanitation_result[0] == -1:
            return (-1, f"default sanitation error {sanitation_result[1]}")

        if sanitation_result[0] == -1:
            return (-1, f"sanitation error: {sanitation_result[1]}")

        self.animation = _animation_class(
            self, _default_update_rate, *(sanitation_result[1])
        )
        print(self.animation)
        self.animation.start()
        return (0, "animation set")

    def __str__(self) -> str:
        return f"chunk: start={self.start}; end={self.end}"


# region animations


class animation:
    def __init__(self, _chunk, _default_update_rate) -> None:
        self.chunk = _chunk
        self.update_rate = _default_update_rate
        self.default_update_rate = _default_update_rate
        self.stopflag = False
        self.animation_thread = None
        self.strip = self.chunk.neopixel
        self.update_count = 0

    @staticmethod
    def sanitize_default_arguments(_default_update_rate):
        default_update_rate = None
        try:
            default_update_rate = int(_default_update_rate)
        except Exception as ex:
            return (-1, "default_update_rate parse error")

        return (0, default_update_rate)

    def stop(self):
        self.update_rate = -1

    def start(self):
        self.update(0)
        self.update_rate = self.default_update_rate

    def update(self):
        print("undefined animation!")


class animation_colorwiperandom(animation):
    def __init__(
        self,
        _chunk,
        _default_update_rate,
        _w,
    ) -> None:
        super().__init__(_chunk, _default_update_rate)
        self.w = _w

    def update(self, tick):
        if self.update_count % self.chunk.num_pixels == 0:
            if type(self.w) == int:
                self.color = util.getRandomRGBColor(self.w)
            else:
                self.color = util.getRandomColor()
        self.strip.setPixelColor(
            self.chunk.start + self.update_count % self.chunk.num_pixels, self.color
        )
        self.update_count += 1

    @staticmethod
    def sanitize_arguments(_w, _update_rate):
        w = None
        wait_ms = None

        try:
            w = int(_w)
        except:
            return (-1, "invalid w")
        try:
            update_rate = int(_update_rate)
        except:
            return (-1, "invalid wait_ms")

        return (0, (w))


class animation_colorwipesequence(animation):
    def __init__(self, _chunk, _default_update_rate, _colors, _wait_ms) -> None:
        super().__init__(_chunk, _default_update_rate)
        self.colors = _colors
        self.wait_ms = _wait_ms
        self.j = 0

    def update(self, tick):
        self.color = self.colors[j % len(self.colors)]
        j += 1
        for i in range(self.chunk.start, self.chunk.end + 1):
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
    def __init__(self, _chunk, _update_rate) -> None:
        animation.__init__(self, _chunk, _update_rate)

    def update(self, tick):
        off_color = Color(0, 0, 0, 0)
        for i in range(self.chunk.start, self.chunk.end + 1):
            self.strip.setPixelColor(i, off_color)

    @staticmethod
    def sanitize_arguments():
        return (0, ())


class animation_cancer(animation):
    def __init__(self, _chunk, _wait_ms) -> None:
        animation.__init__(self, _chunk)
        self.wait_ms = _wait_ms

    def update(self, tick):
        for i in range(self.chunk.start, self.chunk.end + 1):
            self.strip.setPixelColor(i, util.getRandomRGBColor(0))

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

    def update(self, tick):
        for q in range(3):
            for i in range(self.chunk.start, self.chunk.end + 1, 3):
                self.strip.setPixelColor(i + q, self.color)

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

    def update(self, tick):
        for j in range(256):
            for q in range(3):
                for i in range(self.chunk.start, self.chunk.end + 1, 3):
                    self.strip.setPixelColor(i + q, util.wheel((i + j) % 255))

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

    def update(self, tick):
        for j in range(256):
            for i in range(self.chunk.start, self.chunk.end + 1):
                self.strip.setPixelColor(
                    i, util.wheel(((i * 256 // self.chunk.num_pixels) + j) & 255)
                )

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
    # while True:
    #     time.sleep(1)
    #     i += 1
    #     print(f"animating... {strip.chunks[0]}")
    #     if i == 5:
    #         strip.chunks[0].set_animation(animation_rainbowcycle(strip.chunks[0]))

    strip.print_chunk_segmentation()
    #strip.chunks[0].set_animation(animation_off, -1, ())
    while True:
        strip.update()
    time.sleep(1)
    # strip.print_chunk_segmentation()
    time.sleep(5)
    # strip.print_chunk_segmentation()
    time.sleep(50)
