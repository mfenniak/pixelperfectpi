cpuinfo = open("/proc/cpuinfo").read()
if "Raspberry Pi" in cpuinfo:
    EMULATED = False
else:
    EMULATED = True
    print("Emulating RGB matrix...")

import argparse
import asyncio
import importlib
import mqtt
import os
import pytz
import sys
import time
import types
from typing import Literal

config_obj: object | types.ModuleType = object()
try:
    # use import_module to avoid mypy from finding this file only when running local dev
    config_obj = importlib.import_module("config")
except ModuleNotFoundError:
    pass

if EMULATED:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions # type: ignore
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions # type: ignore


class SampleBase(object):
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument("-r", "--led-rows", action="store", help="Display rows. 16 for 16x32, 32 for 32x32. Default: 32", default=32, type=int)
        self.parser.add_argument("--led-cols", action="store", help="Panel columns. Typically 32 or 64. (Default: 32)", default=32, type=int)
        self.parser.add_argument("-c", "--led-chain", action="store", help="Daisy-chained boards. Default: 1.", default=1, type=int)
        self.parser.add_argument("-P", "--led-parallel", action="store", help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1", default=1, type=int)
        self.parser.add_argument("-p", "--led-pwm-bits", action="store", help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
        self.parser.add_argument("-b", "--led-brightness", action="store", help="Sets brightness level. Default: 100. Range: 1..100", default=100, type=int)
        self.parser.add_argument("-m", "--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm" , choices=['regular', 'regular-pi1', 'adafruit-hat', 'adafruit-hat-pwm'], type=str)
        self.parser.add_argument("--led-scan-mode", action="store", help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)", default=1, choices=range(2), type=int)
        self.parser.add_argument("--led-pwm-lsb-nanoseconds", action="store", help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130", default=130, type=int)
        self.parser.add_argument("--led-show-refresh", action="store_true", help="Shows the current refresh rate of the LED panel")
        self.parser.add_argument("--led-slowdown-gpio", action="store", help="Slow down writing to GPIO. Range: 0..4. Default: 1", default=1, type=int)
        self.parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation")
        self.parser.add_argument("--led-rgb-sequence", action="store", help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB", type=str)
        self.parser.add_argument("--led-pixel-mapper", action="store", help="Apply pixel mappers. e.g \"Rotate:90\"", default="", type=str)
        self.parser.add_argument("--led-row-addr-type", action="store", help="0 = default; 1=AB-addressed panels; 2=row direct; 3=ABC-addressed panels; 4 = ABC Shift + DE direct", default=0, type=int, choices=[0,1,2,3,4])
        self.parser.add_argument("--led-multiplexing", action="store", help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven... (Default: 0)", default=0, type=int)
        self.parser.add_argument("--led-panel-type", action="store", help="Needed to initialize special panels. Supported: 'FM6126A'", default="", type=str)
        self.parser.add_argument("--led-no-drop-privs", dest="drop_privileges", help="Don't drop privileges from 'root' after initializing the hardware.", action='store_false')
        self.parser.add_argument("--ical-url", dest="ical_url", help="iCal URL", default=None, type=str)
        self.parser.add_argument("--font-path", dest="font_path", help="path to pil font files", default=None, type=str)
        self.parser.add_argument("--display-tz", dest="display_tz", help="Timezone to display, IANA notation eg. America/Edmonton", default=None, type=str)
        self.parser.set_defaults(drop_privileges=True)

        mqtt.config_arg_parser(self.parser)

        self.state: Literal["ON"] | Literal["OFF"] = "ON"
        self.turn_on_event: asyncio.Event | None = None
        self.shutdown_event = asyncio.Event()

    ical_url = property(lambda self: getattr(config_obj, 'ICAL_URL', self.args.ical_url))
    font_path = property(lambda self: getattr(config_obj, 'FONT_PATH', self.args.font_path) or "./fonts")
    display_tz = property(lambda self: pytz.timezone(getattr(config_obj, 'DISPLAY_TZ', self.args.display_tz) or "America/Edmonton"))

    async def run(self) -> None:
        raise NotImplemented

    async def turn_on(self) -> None:
        if self.state == "ON":
            return
        assert self.turn_on_event is not None
        self.state = "ON"
        self.turn_on_event.set()
        await self.mqtt.status_update(self.state)

    async def turn_off(self) -> None:
        if self.state == "OFF":
            return
        assert self.turn_on_event is None
        self.turn_on_event = asyncio.Event()
        self.state = "OFF"
        await self.mqtt.status_update(self.state)

    def process(self) -> None:
        self.args = self.parser.parse_args()

        options = RGBMatrixOptions()

        if self.args.led_gpio_mapping != None:
            options.hardware_mapping = self.args.led_gpio_mapping
        options.rows = getattr(config_obj, 'LED_ROWS', self.args.led_rows)
        options.cols = getattr(config_obj, 'LED_COLS', self.args.led_cols)
        options.chain_length = self.args.led_chain
        options.parallel = self.args.led_parallel
        options.row_address_type = self.args.led_row_addr_type
        options.multiplexing = self.args.led_multiplexing
        options.pwm_bits = self.args.led_pwm_bits
        options.brightness = self.args.led_brightness
        options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
        options.led_rgb_sequence = self.args.led_rgb_sequence
        options.pixel_mapper_config = self.args.led_pixel_mapper
        options.panel_type = self.args.led_panel_type

        if self.args.led_show_refresh:
            options.show_refresh_rate = 1

        led_slowdown_gpio = getattr(config_obj, 'LED_SLOWDOWN_GPIO', self.args.led_slowdown_gpio)
        if led_slowdown_gpio != None:
            options.gpio_slowdown = led_slowdown_gpio
        if self.args.led_no_hardware_pulse:
            options.disable_hardware_pulsing = True
        if not self.args.drop_privileges:
            options.drop_privileges=False

        mqtt_config = mqtt.get_config(self.args)
        self.mqtt = mqtt.MqttServer(mqtt_config, self, self.shutdown_event)

        self.rgbmatrixOptions = options
        self.matrix = None
        try:
            # Start loop
            print("Press CTRL-C to stop sample")
            asyncio.run(self.async_run())
        except KeyboardInterrupt:
            self.shutdown_event.set()
            print("Exiting\n")
            sys.exit(0)

    def pre_run(self) -> None:
        raise NotImplemented

    async def update_data(self) -> None:
        raise NotImplemented

    async def create_canvas(self, matrix: RGBMatrix) -> None:
        raise NotImplemented

    async def draw_frame(self, matrix: RGBMatrix) -> None:
        raise NotImplemented

    async def async_run(self) -> None:
        self.mqtt.start()
        self.pre_run()
        await self.main_loop()

    async def main_loop(self) -> None:
        while True:
            await self.update_data()

            if self.state == "OFF":
                if self.matrix is not None:
                    self.matrix.Clear()
                    del self.matrix
                    self.matrix = None

                # Wake when we're turned on...
                assert self.turn_on_event is not None
                turn_on_event_task = asyncio.create_task(self.turn_on_event.wait())
                # Wake after a bit just to do an update_data call...
                sleep_task = asyncio.create_task(asyncio.sleep(120))
                # Wait until either wake condition; doesn't matter which.
                await asyncio.wait([ turn_on_event_task, sleep_task ], return_when=asyncio.FIRST_COMPLETED)

            elif self.state == "ON":
                if self.matrix is None:
                    self.matrix = RGBMatrix(options = self.rgbmatrixOptions)
                    await self.create_canvas(self.matrix)

                await self.draw_frame(self.matrix)
                await asyncio.sleep(0.1)
