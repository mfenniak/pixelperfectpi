#!/usr/bin/env python

from samplebase import SampleBase, EMULATED

if EMULATED:
    from RGBMatrixEmulator import graphics
else:
    from rgbmatrix import graphics
from rgbmatrix import font_path
from lxml import etree
from PIL import Image, ImageFont, ImageDraw, ImageColor
import time
import asyncio
import aiohttp
import traceback
import re
import icalendar
import datetime
import pytz
import random
import recurring_ical_events
import os.path

RGB_RE = re.compile(r"rgb\((?P<red>[0-9]+),(?P<green>[0-9]+),(?P<blue>[0-9]+)\)")


class DataResolver(object):
    def __init__(self, refresh_interval):
        jitter_frac = 1 + (random.random() * 0.2) # always jitter longer so we don't drop below refresh_interval
        self.refresh_interval = (refresh_interval * jitter_frac)
        self.last_refresh = 0
        self.lock = asyncio.Lock()
        self.data = None

    async def maybe_refresh(self, now):
        delta = now - self.last_refresh
        if delta > self.refresh_interval:
            try:
                await asyncio.wait_for(self.lock.acquire(), timeout=0.0000001)
                try:
                    await self.refresh()
                    self.last_refresh = now
                finally:
                    self.lock.release()
            except TimeoutError:
                pass

    async def refresh(self):
        try:
            cr = self.do_collection()
            self.data = await cr
        except:
            # FIXME: log error
            print("do_collection error occurred")
            traceback.print_exc()
            self.data = None


class StaticDataResolver(object):
    def __init__(self, static_data=None):
        super().__init__()
        self.data = static_data

    async def maybe_refresh(self, now):
        return


class PurpleAirDataResolver(DataResolver):
    def __init__(self):
        super().__init__(refresh_interval=60)

    async def do_collection(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://10.156.95.135/json') as response:
                if response.status != 200:
                    raise Exception(f"Unexpected status code: {response.status}")
                purpleair = await response.json()

                color = purpleair["p25aqic"] # string, eg. rgb(87,237,0)
                m = RGB_RE.match(color)
                red, green, blue = int(m.group("red")), int(m.group("green")), int(m.group("blue")) 
                purpleair["p25aqic"] = (red, green, blue)

                purpleair["p25aqiavg"] = (purpleair['pm2.5_aqi'] + purpleair['pm2.5_aqi_b']) / 2

                temp_f = purpleair["current_temp_f"]
                # PurpleAir's API has a "Raw temperature".  https://community.purpleair.com/t/purpleair-sensors-functional-overview/150
                # They correct it -8 deg F to get a good approximation of ourdoor ambient temp.
                temp_f -= 8
                temp_c = (temp_f - 32) * 5 / 9
                purpleair["current_temp_c"] = temp_c

                # {'SensorId': '...',
                # 'p25aqic_b': 'rgb(55,234,0)'
                # 'pm2.5_aqi_b': 30
                # 'pm2.5_aqi': 35, 
                # 'p25aqic': 'rgb(87,237,0)', 
                # 'current_temp_f': 62, 
                return purpleair


class EnvironmentCanadaDataResolver(DataResolver):
    def __init__(self):
        super().__init__(refresh_interval=3600)

    async def fetch_xml(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://dd.weather.gc.ca/citypage_weather/xml/AB/s0000047_e.xml') as response:
                if response.status != 200:
                    raise Exception(f"Unexpected status code: {response.status}")
                return await response.read()

    async def do_collection(self):
        xml_content = await self.fetch_xml()
        root = etree.fromstring(xml_content)
        elements = root.xpath("/siteData/forecastGroup/forecast")
        # FIXME: handle missing/malformed data; no [0] without a good error; just set data to None
        first_forecast = elements[0]
        forecast_name = first_forecast.xpath("period[@textForecastName]")[0].values()[0] # "Today", "Tonight"
        temperatures = first_forecast.xpath("temperatures/temperature")
        text_summary = first_forecast.xpath("abbreviatedForecast/textSummary/text()")[0]
        first_temperature = temperatures[0]

        sunrise = root.xpath("/siteData/riseSet/dateTime[@zone='UTC' and @name='sunrise']/timeStamp/text()")[0]
        (sunrise_year, sunrise_month, sunrise_day, sunrise_hour, sunrise_minute) = (sunrise[:4], sunrise[4:6], sunrise[6:8], sunrise[8:10], sunrise[10:12])
        sunrise = datetime.datetime(int(sunrise_year), int(sunrise_month), int(sunrise_day), int(sunrise_hour), int(sunrise_minute), tzinfo=pytz.utc)

        sunset = root.xpath("/siteData/riseSet/dateTime[@zone='UTC' and @name='sunset']/timeStamp/text()")[0]
        (sunset_year, sunset_month, sunset_day, sunset_hour, sunset_minute) = (sunset[:4], sunset[4:6], sunset[6:8], sunset[8:10], sunset[10:12])
        sunset = datetime.datetime(int(sunset_year), int(sunset_month), int(sunset_day), int(sunset_hour), int(sunset_minute), tzinfo=pytz.utc)

        # Future: precipitation, snowLevel, windChill, uv, wind?
        data = {
            "forecast": {
                "name": forecast_name, # Today, Tonight
                "type": first_temperature.get("class"), # high/low
                "deg_c": float(first_temperature.text),
                "text_summary": text_summary
            },
            "sunrise": sunrise,
            "sunset": sunset,
        }
        return data


class CalendarDataResolver(DataResolver):
    def __init__(self, ical_url, display_tz):
        super().__init__(refresh_interval=3600)
        self.ical_url = ical_url
        self.display_tz = display_tz

    async def fetch_ical(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.ical_url) as response:
                if response.status != 200:
                    raise Exception(f"Unexpected status code: {response.status}")
                return await response.read()

    async def do_collection(self):
        ical_content = await self.fetch_ical()
        calendar = icalendar.Calendar.from_ical(ical_content)
        future_events = []

        now = datetime.datetime.now(pytz.utc) # datetime.timezone.utc)
        today = datetime.date.today()

        start_date = now
        end_date = now + datetime.timedelta(days=14)
        events = recurring_ical_events.of(calendar).between(start_date, end_date)
        for event in events:
            dtstart = event.get("dtstart").dt
            if isinstance(dtstart, datetime.datetime):
                if dtstart > now:
                    future_events.append((dtstart.astimezone(self.display_tz), str(event.get("SUMMARY"))))
            elif isinstance(dtstart, datetime.date):
                # Show "today" events until 8am, then move on
                dtstart_morning = datetime.datetime.combine(dtstart, datetime.time(8, 0, 0)).astimezone(self.display_tz)
                if dtstart_morning > now:
                    start = datetime.datetime.combine(dtstart, datetime.time()).astimezone(self.display_tz)
                    future_events.append((start, str(event.get("SUMMARY"))))
            else:
                print("unexpected dt type", repr(dtstart))

        future_cutoff = now + datetime.timedelta(days=7)
        near_future_events = [x for x in future_events if x[0] < future_cutoff]
        near_future_events = sorted(near_future_events, key=lambda event: event[0])

        return {
            "future_events": near_future_events
        }


class DrawPanel(object):
    def __init__(self, x, y, w, h, font_path, data_resolver, **kwargs):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.font_path = font_path
        self.buffer = Image.new("RGB", (self.w, self.h))
        self.imagedraw = ImageDraw.Draw(self.buffer)
        self.pil_font = None
        self.data_resolver = data_resolver

    def load_font(self, name):
        self.pil_font = ImageFont.load(os.path.join(self.font_path, f"{name}.pil"))

    def frame_count(self, **kwargs):
        return 1

    def draw(self, parent_buffer, **kwargs):
        self.do_draw(**kwargs)
        parent_buffer.paste(self.buffer, box=(self.x, self.y))

    def fill(self, color):
        self.buffer.paste(color, box=(0,0,self.w,self.h))

    # halign - left, center, right
    # valign - top, middle, bottom
    def draw_text(self, color, text, halign="center", valign="middle"):
        if self.pil_font is None:
            raise Exception("must call load_font first")

        # measure the total width of the text...
        (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), text, font=self.pil_font, spacing=0, align="left")
        if right <= self.w:
            # it will fit in a single-line; nice and easy peasy...
            text_height = bottom
            if valign == "top":
                text_y = 0
            elif valign == "bottom":
                text_y = self.h - bottom
            else: # middle
                text_y = (self.h - text_height) // 2
            text_width = right
            if halign == "left":
                text_x = 0
            elif halign == "right":
                text_x = self.w - text_width
            else: # center
                text_x = (self.w - text_width) // 2
            self.imagedraw.multiline_text((text_x, text_y), text, fill=color, font=self.pil_font, spacing=0, align=halign)
            return

        # alright... let's just go line-by-line then, shall we.  First find the most text that will fit into one line,
        # word-by-word.
        lines = []
        text_words = text.split(" ")
        line = ""
        height_total = 0
        widest_line = 0
        while True:
            if len(text_words) == 0:
                # Ran out of words.
                if line != "":
                    height_total += bottom
                    lines.append(line)
                    (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), line, font=self.pil_font, spacing=0, align="left")
                    widest_line = max(widest_line, right)
                break

            next_word = text_words[0]
            proposed_line = line
            if proposed_line != "":
                proposed_line += " "
            proposed_line += next_word
            
            # will "proposed_line" fit onto a line?
            (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), proposed_line, font=self.pil_font, spacing=0, align="left")
            if right > self.w:
                height_total += bottom
                # no, proposed_line is too big; we'll make do with the last `line`
                if line != "":
                    lines.append(line)
                    (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), line, font=self.pil_font, spacing=0, align="left")
                    widest_line = max(widest_line, right)
                    line = ""
                    # leave next_word in text_words and keep going
                else:
                    # next_word by itself won't fit on a line; well, we can't skip the middle of a sentence so we'll
                    # just consume it regardless as it's own line.  Ignore it for widest_line calc.
                    lines.append(next_word)
                    text_words = text_words[1:]
            else:
                # yes, it will fit on the line
                line = proposed_line
                text_words = text_words[1:]

        new_text = "\n".join(lines)

        text_height = height_total
        if valign == "top":
            text_y = 0
        elif valign == "bottom":
            text_y = max(0, self.h - bottom)
        else: # middle
            text_y = max(0, (self.h - text_height) // 2)
        text_width = widest_line
        if halign == "left":
            text_x = 0
        elif halign == "right":
            text_x = max(0, self.w - text_width)
        else: # center
            text_x = max(0, (self.w - text_width) // 2)

        self.imagedraw.multiline_text((text_x, text_y), new_text, fill=color, font=self.pil_font, spacing=0, align=halign)


class MultiPanelPanel(DrawPanel):
    def __init__(self, panel_constructors, time_per_frame=5, *args, **kwargs):
        super().__init__(data_resolver=StaticDataResolver(), *args, **kwargs)
        inner_kwargs = kwargs.copy()
        # same width & height, but don't inherit the x/y position
        inner_kwargs['x'] = 0
        inner_kwargs['y'] = 0
        self.panels = [
            constructor(**inner_kwargs) for constructor in panel_constructors
        ]
        self.time_per_frame = time_per_frame

    def do_draw(self, now, **kwargs):
        # First; get a snapshot of the data for each panel so that it doesn't change while we're calculating this.
        panel_datas = [x.data_resolver.data for x in self.panels]

        # Ask each panel how many frames they will have, considering their data.
        frame_count = [x.frame_count(data=panel_datas[i]) for i, x in enumerate(self.panels)]

        # Based upon the total number of frames on all panels, and the time, calculate the active frame.
        total_frames = sum(frame_count)

        if total_frames == 0:
            self.fill((0, 0, 0))
            return

        active_frame = int(now / self.time_per_frame) % total_frames

        # Find the panel for that frame, and the index of that frame in that panel.
        running_total = 0
        target_panel_index = None
        target_frame_index = None
        for panel_index, frame_count in enumerate(frame_count):
            maybe_frame_index = active_frame - running_total
            if maybe_frame_index < frame_count:
                target_panel_index = panel_index
                target_frame_index = maybe_frame_index
                break
            running_total += frame_count

        self.panels[target_panel_index].draw(self.buffer, now=now, data=panel_datas[target_panel_index], frame=target_frame_index)


class TimeComponent(DrawPanel):
    def __init__(self, *args, **kwargs):
        super().__init__(data_resolver=StaticDataResolver(), *args, **kwargs)
        self.load_font("7x13")

    def do_draw(self, now, **kwargs):
        self.fill((0, 0, 0))

        hue = int(now*50 % 360)
        red, green, blue = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")
        color = (red, green, blue)

        timestr = time.strftime("%-I:%M")
        if int(now % 2) == 0:
            timestr = timestr.replace(":", " ")
        self.draw_text(color, timestr, halign="right")


class DayOfWeekComponent(DrawPanel):
    def __init__(self, *args, **kwargs):
        super().__init__(data_resolver=StaticDataResolver(), *args, **kwargs)
        self.load_font("7x13")

    def do_draw(self, now, **kwargs):
        self.fill((0, 0, 0))

        hue = int(now*50 % 360)
        red, green, blue = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")
        color = (red, green, blue)

        timestr = time.strftime("%a")
        self.draw_text(color, timestr)


class CurrentTemperatureComponent(DrawPanel):
    def __init__(self, purpleair, *args, **kwargs):
        super().__init__(data_resolver=purpleair, *args, **kwargs)
        self.load_font("7x13")

    def frame_count(self, data):
        if data == None:
            return 0
        else:
            return 1

    def do_draw(self, data, **kwargs):
        self.fill((0, 0, 0))
        if data is None:
            return
        curr_c = data["current_temp_c"]
        self.draw_text((128,128,128), f"{curr_c:.0f}°")


class AqiComponent(DrawPanel):
    def __init__(self, purpleair, *args, **kwargs):
        super().__init__(data_resolver=purpleair, *args, **kwargs)
        self.load_font("7x13")

    def frame_count(self, data):
        if data == None:
            return 0
        else:
            return 1

    def do_draw(self, data, **kwargs):
        self.fill((0, 16, 0))
        (red, green, blue) = data["p25aqic"]
        textColor = (red, green, blue)
        aqi = data['p25aqiavg']
        self.draw_text(textColor, f"AQI {aqi:.0f}")


class WeatherForecastComponent(DrawPanel):
    def __init__(self, env_canada, *args, **kwargs):
        super().__init__(data_resolver=env_canada, *args, **kwargs)
        self.load_font("4x6")

    def frame_count(self, data):
        if data == None:
            return 0
        else:
            return 1

    def do_draw(self, data, **kwargs):
        self.fill((16, 0, 0))
        n = data['forecast']['name']
        s = data['forecast']['text_summary']
        t = data['forecast']['type'].capitalize()
        deg_c = data['forecast']['deg_c']
        self.draw_text((255, 255, 255), f"{n} {s} {t} {deg_c:.0f}°")


class SunForecastComponent(DrawPanel):
    def __init__(self, env_canada, display_tz, *args, **kwargs):
        super().__init__(data_resolver=env_canada, *args, **kwargs)
        self.display_tz = display_tz
        self.load_font("5x8")

    def frame_count(self, data):
        if data == None:
            return 0
        else:
            return 1

    def do_draw(self, now, data, **kwargs):
        now = datetime.datetime.now(self.display_tz)
        sunrise = data['sunrise']
        sunset = data['sunset']

        if sunrise > now and sunrise < sunset:
            self.fill((16, 16, 0))
            sun = "Sunrise"
            color = (255,167,0)
            dt = sunrise.astimezone(self.display_tz).strftime("%-I:%M")
        else:
            self.fill((0, 0, 16))
            sun = "Sunset"
            color = (80,80,169)
            dt = sunset.astimezone(self.display_tz).strftime("%-I:%M")
        self.draw_text(color, f"{sun} at {dt}")


class CalendarComponent(DrawPanel):
    def __init__(self, calendar, display_tz, *args, **kwargs):
        super().__init__(data_resolver=calendar, *args, **kwargs)
        self.display_tz = display_tz
        self.load_font("4x6")

    def frame_count(self, data):
        if data == None:
            return 0
        return min(len(data["future_events"]), 3) # no more than this many events

    def do_draw(self, now, data, frame, **kwargs):
        self.fill((0, 0, 16))

        # FIXME: color is synced to the time, but, only by copy-and-paste
        hue = int(now*50 % 360)
        red, green, blue = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")
        textColor = (red, green, blue)

        (dt, summary) = data["future_events"][frame]

        preamble = ""
        now = datetime.datetime.now(self.display_tz)

        if dt.time() == datetime.time(0,0,0):
            # full day event probably
            if dt.date() == now.date():
                preamble = "tdy"
            elif dt.date() == (now + datetime.timedelta(days=1)).date():
                preamble = dt.strftime("tmw")
            elif (dt - now) < datetime.timedelta(days=7):
                preamble = dt.strftime("%a")
            else:
                preamble = dt.strftime("%a %-d")
        else:
            # timed event
            if dt.date() == now.date():
                preamble = dt.strftime("%-I%p")
            elif dt.date() == (now + datetime.timedelta(days=1)).date():
                preamble = dt.strftime("tmw %-I%p")
            elif (dt - now) < datetime.timedelta(days=7):
                preamble = dt.strftime("%a %-I%p")
            else:
                preamble = dt.strftime("%a %-d")

        if preamble.endswith("M"): # PM/AM -> P/A; no strftime option for that
            preamble = preamble[:-1]
        if preamble.endswith("P") or preamble.endswith("A"): # lowercase this
            preamble = preamble[:-1] + preamble[-1].lower()

        text = f"{preamble}: {summary}"
        self.draw_text(textColor, text.encode("ascii", errors="ignore").decode("ascii"))


# TODO List:
# - Add icons - like a lightning bolt for power, or, sun^ sunv for high and low?
# - Animations - don't know where, when, but let's use all the pixels sometimes
# - Add capability for panels to have subpanels, since drawing ops are full panel size
# - Add something with an icon/image -- maybe the weather forecast
# New data:
# - Power: Usage, Solar Generation
# - Home Assistant: Back door / Garage door / etc. Open
# - Google Location: Distance to Mathieu?
# - Home Assistant: Presence
# - Countdown - France Flag & # days to France
# - Errors from any of the other data collectors / displayers
# - anxi - Any errors on Prometheus?


class Clock(SampleBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def pre_run(self):
        self.purpleair = PurpleAirDataResolver()
        self.env_canada = EnvironmentCanadaDataResolver()
        self.calendar = CalendarDataResolver(self.ical_url, self.display_tz)
        self.data_resolvers = [
            self.purpleair,
            self.env_canada,
            self.calendar,
        ]
        self.background_tasks = set()

        addt_config={
            "font_path": self.font_path,
            "display_tz": self.display_tz,
        }
        self.time_component = TimeComponent(29, 0, 35, 13, **addt_config)
        self.curr_component = MultiPanelPanel(
            panel_constructors=[
                lambda **kwargs: CurrentTemperatureComponent(purpleair=self.purpleair, **kwargs),
                lambda **kwargs: DayOfWeekComponent(**kwargs),
            ],
            time_per_frame=5,
            x=0, y=0, w=29, h=13,
            **addt_config,
        )
        self.lower_panels = MultiPanelPanel(
            panel_constructors=[
                lambda **kwargs: AqiComponent(purpleair=self.purpleair, **kwargs),
                lambda **kwargs: CalendarComponent(calendar=self.calendar, **kwargs),
                lambda **kwargs: WeatherForecastComponent(env_canada=self.env_canada, **kwargs),
                lambda **kwargs: SunForecastComponent(env_canada=self.env_canada, **kwargs),
            ],
            time_per_frame=5,
            x=0, y=13, w=64, h=19,
            **addt_config,
        )

    async def create_canvas(self, matrix):
        self.offscreen_canvas = matrix.CreateFrameCanvas()
        self.buffer = Image.new("RGB", (self.offscreen_canvas.width, self.offscreen_canvas.height))

    async def update_data(self):
        now = time.time()
        for data_resolver in self.data_resolvers:
            task = asyncio.create_task(data_resolver.maybe_refresh(now))
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)

    async def draw_frame(self, matrix):
        now = time.time()
        self.time_component.draw(self.buffer, now=now)
        self.curr_component.draw(self.buffer, now=now)
        self.lower_panels.draw(self.buffer, now=now)
        self.offscreen_canvas.SetImage(self.buffer, 0, 0)

        self.offscreen_canvas = matrix.SwapOnVSync(self.offscreen_canvas)


# Main function
if __name__ == "__main__":
    run_text = Clock()
    if (not run_text.process()):
        run_text.print_help()
