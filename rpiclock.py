#!/usr/bin/env python

from samplebase import SampleBase, EMULATED

if EMULATED:
    from RGBMatrixEmulator import graphics
else:
    from rgbmatrix import graphics
from rgbmatrix import font_path
from lxml import etree
from PIL.ImageColor import getrgb
import time
import asyncio
import aiohttp
import traceback
import re
import icalendar
import datetime
import pytz


RGB_RE = re.compile(r"rgb\((?P<red>[0-9]+),(?P<green>[0-9]+),(?P<blue>[0-9]+)\)")


class DataResolver(object):
    def __init__(self, refresh_interval):
        self.refresh_interval = refresh_interval
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


class PurpleAirDataResolver(DataResolver):
    def __init__(self):
        super().__init__(refresh_interval=60)

    async def do_collection(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://10.156.95.135/json') as response:
                if response.status != 200:
                    raise Exception(f"Unexpected status code: {response.status}")
                purpleair = await response.json()
                # print("PurpleAirDataResolver.do_collection", purpleair)

                color = purpleair["p25aqic"] # rgb(87,237,0)
                m = RGB_RE.match(color)
                red, green, blue = int(m.group("red")), int(m.group("green")), int(m.group("blue")) 
                purpleair["p25aqic"] = (red, green, blue)

                purpleair["p25aqiavg"] = (purpleair['pm2.5_aqi'] + purpleair['pm2.5_aqi_b']) / 2

                # {'SensorId': '...',
                # 'p25aqic_b': 'rgb(55,234,0)'
                # 'pm2.5_aqi_b': 30
                # 'pm2.5_aqi': 35, 
                # 'p25aqic': 'rgb(87,237,0)', 
                # 'current_temp_f': 62, 
                return purpleair


class EnvironmentCanadaDataResolver(DataResolver):
    def __init__(self):
        super().__init__(refresh_interval=1800)

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
        # FIXME: handle missing/malformed data; no [0] without a good error
        first_forecast = elements[0]
        forecast_name = first_forecast.xpath("period[@textForecastName]")[0].values()[0] # "Today", "Tonight"
        temperatures = first_forecast.xpath("temperatures/temperature")
        first_temperature = temperatures[0]
        # Future: precipitation, snowLevel, windChill, uv, wind?
        data = {
            "forecast": {
                "name": forecast_name, # Today, Tonight
                "type": first_temperature.get("class"), # high/low
                "deg_c": float(first_temperature.text),
            }
        }
        print("EnvironmentCanadaDataResolver.do_collection", repr(data))
        return data


class CalendarDataResolver(DataResolver):
    def __init__(self, ical_url):
        super().__init__(refresh_interval=1800)
        self.ical_url = ical_url

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
        target_tz = pytz.timezone("America/Edmonton")
        today = datetime.date.today()

        for event in calendar.walk('VEVENT'):
            dtstart = event.get("dtstart").dt
            if isinstance(dtstart, datetime.datetime):
                if dtstart > now:
                    future_events.append((dtstart.astimezone(target_tz), str(event.get("SUMMARY"))))
            elif isinstance(dtstart, datetime.date):
                if dtstart >= today:
                    start = datetime.datetime.combine(dtstart, datetime.time()).astimezone(target_tz)
                    future_events.append((start, str(event.get("SUMMARY"))))
            else:
                print("unexpected dt type", repr(dtstart))

        future_cutoff = now + datetime.timedelta(days=7)
        near_future_events = [x for x in future_events if x[0] < future_cutoff]
        near_future_events = sorted(near_future_events, key=lambda event: event[0])
        print("near_future_events", near_future_events)

        return {
            "future_events": near_future_events
        }


class DashboardComponent(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self, canvas, now):
        self.canvas = canvas
        self.do_draw(now)
        self.canvas = None

    def fill(self, color):
        for x in range(self.x, self.x + self.w):
            for y in range(self.y, self.y + self.h):
                self.canvas.SetPixel(x, y, color.red, color.green, color.blue)

    def draw_text(self, font, x, y, color, text):
        # FIXME: width/height limits not implemented
        return graphics.DrawText(self.canvas, font, self.x + x, self.y + y + font.height - (font.height - font.baseline), color, text)


class TimeComponent(DashboardComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = graphics.Font()
        self.font.LoadFont(font_path + "/7x13.bdf")

    def do_draw(self, now):
        # self.fill(graphics.Color(255, 255, 255))
        hue = int(now*50 % 360)
        # print("hue", hue)
        red, green, blue = getrgb(f"hsl({hue}, 100%, 50%)")
        color = graphics.Color(red, green, blue)
        timestr = time.strftime("%I:%M")
        if timestr[0] == "0":
            timestr = " " + timestr[1:]
        if int(now % 2) == 0:
            timestr = timestr.replace(":", " ")
        self.draw_text(self.font, 0, 0, color, timestr)


class AqiComponent(DashboardComponent):
    def __init__(self, purpleair, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.purpleair = purpleair
        self.font = graphics.Font()
        self.font.LoadFont(font_path + "/7x13.bdf")

    def do_draw(self, now):
        # self.fill(graphics.Color(255, 0, 255))
        pa = self.purpleair.data
        if pa:
            (red, green, blue) = pa["p25aqic"]
            textColor = graphics.Color(red, green, blue)
            aqi = pa['p25aqiavg']
            self.draw_text(self.font, 8, 0, textColor, f"AQI {aqi:>3.0f}")


class CalendarComponent(DashboardComponent):
    def __init__(self, calendar, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calendar = calendar
        self.font = graphics.Font()
        self.font.LoadFont(font_path + "/4x6.bdf")

        # FIXME: make a component able to opt-out of being drawn if it has no data, rather than being blank

    def do_draw(self, now):
        # self.fill(graphics.Color(255, 0, 255))

        if self.calendar.data is None:
            return

        # FIXME: synced to the time, but, only by copy-and-paste
        hue = int(now*50 % 360)
        # print("hue", hue)
        red, green, blue = getrgb(f"hsl({hue}, 100%, 50%)")
        textColor = graphics.Color(red, green, blue)

        (dt, summary) = self.calendar.data["future_events"][0]

        preamble = ""
        target_tz = pytz.timezone("America/Edmonton")
        now = datetime.datetime.now(target_tz)

        # print("now", now)
        # print("now.date", now.date())
        # print("dt", dt)
        # print("dt.date", dt.date())
        # print("tom.date", (now + datetime.timedelta(days=1)).date())

        if dt.date() == now.date():
            preamble = dt.strftime("%-I%p")
        elif dt.date() == (now + datetime.timedelta(days=1)).date():
            preamble = dt.strftime("Tom %-I%p")
        elif (dt - now) < datetime.timedelta(days=7):
            preamble = dt.strftime("%a %-I%p")
        else:
            preamble = dt.strftime("%a %-d")

        if preamble.endswith("M"): # PM/AM -> P/A; no strftime option for that
            preamble = preamble[:-1]


        text = f"{preamble} {summary}"

        x = 0
        y = 0
        for c in text:
            width = self.draw_text(self.font, x, y, textColor, c.encode("ascii", errors="ignore").decode("ascii"))
            x += (width or 0)
            if x > self.w:
                y += self.font.height
                x = 0
                # redraw character that was at least partially off-screen..
                width = self.draw_text(self.font, x, y, textColor, c.encode("ascii", errors="ignore").decode("ascii"))
                x += (width or 0)


# TODO List:
# - Create a "measure text" function, center text
# - Add icons - like a lightning bolt for power, or, sun^ sunv for high and low?
# - Animations - don't know where, when, but let's use all the pixels sometimes
# - Jitter the data loader times -- if two things are both 1800s, don't want them to occur at the same time
# New data:
# - Weather Forecast: Upcoming High/Low
# - Weather Forecast: Upcoming Rain
# - Date w/ time -- eg. "Tue 6:53"
# - Times: Sunrise, Sunset
# - Calendar - pull upcoming events in the next 1-3d, use super small font to draw
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
        self.envcanada = EnvironmentCanadaDataResolver()
        self.calendar = CalendarDataResolver(self.ical_url)
        self.data_resolvers = [
            self.purpleair,
            self.envcanada,
            self.calendar,
        ]

    async def run(self):
        background_tasks = set()

        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont(font_path + "/7x13.bdf")

        time_component = TimeComponent(29, 0, 35, 13)

        lower_panels = [
            AqiComponent(self.purpleair, 0, 13, 64, 19),
            CalendarComponent(self.calendar, 0, 13, 64, 19),
        ]
        # aqi_component =  # 0, 32, 64, 32)
        # hue = 0

        while True:
            now = time.time()
            for data_resolver in self.data_resolvers:
                task = asyncio.create_task(data_resolver.maybe_refresh(now))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)

            offscreen_canvas.Clear()

            time_component.draw(offscreen_canvas, now)
            
            time_per_panel = 5
            lower_panels[int(now / time_per_panel) % len(lower_panels)].draw(offscreen_canvas, now)


            # aqi_component.draw(offscreen_canvas, now)

            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            await asyncio.sleep(0.1)


# http://10.156.95.135/json
# {'SensorId': '...',
# 'p25aqic_b': 'rgb(55,234,0)'
# 'pm2.5_aqi_b': 30
# 'p25aqic': 'rgb(87,237,0)', 
# 'pm2.5_aqi': 35, 
# 'current_temp_f': 62, 
# 'DateTime': '2023/09/14T14:34:30z',
# 'Geo': '...',
# 'Mem': 9528,
# 'memfrag': 43,
# 'memfb': 5776,
# 'memcs': 168,
# 'Id': 8540,
# 'lat': ...,
# 'lon': ...,
# 'Adc': 0.0,
# 'loggingrate': 15,
# 'place': 'outside',
# 'version': '7.04', 
# 'uptime': 503476, 
# 'rssi': -65, 
# 'period': 120, 
# 'httpsuccess': 8528, 
# 'httpsends': 8530, 
# 'hardwareversion': '3.0', 
# 'hardwarediscovered': '3.0+OPENLOG+NO-DISK+RV3028+BME68X+PMSX003-A+PMSX003-B', 
# 'current_humidity': 36, 
# 'current_dewpoint_f': 35, 
# 'pressure': 899.9
# 'current_temp_f_680': 62
# 'current_humidity_680': 36
# 'current_dewpoint_f_680': 35
# 'pressure_680': 899.9
# 'gas_680': 86.84
# 'pm1_0_cf_1_b': 5.12
# 'p_0_3_um_b': 983.43
# 'pm2_5_cf_1_b': 7.19
# 'p_0_5_um_b': 289.84, 
# 'pm10_0_cf_1_b': 8.17, 
# 'p_1_0_um_b': 34.03, 
# 'pm1_0_atm_b': 5.12, 
# 'p_2_5_um_b': 4.97, 
# 'pm2_5_atm_b': 7.19, 
# 'p_5_0_um_b': 1.28, 
# 'pm10_0_atm_b': 8.17, 
# 'p_10_0_um_b': 0.59, 
# 'pm1_0_cf_1': 6.35, 
# 'p_0_3_um': 1279.63, 
# 'pm2_5_cf_1': 8.42, 
# 'p_0_5_um': 365.6, 
# 'pm10_0_cf_1': 9.56, 
# 'p_1_0_um': 38.49, 
# 'pm1_0_atm': 6.35, 
# 'p_2_5_um': 4.65, 
# 'pm2_5_atm': 8.42, 
# 'p_5_0_um': 1.47, 
# 'pm10_0_atm': 9.56, 
# 'p_10_0_um': 0.63, 
# 'pa_latency': 244, 
# 'response': 401,
# 'response_date': 1694702059,
# 'latency': 256,
# 'wlstate': 'Connected',
# 'status_0': 2,
# 'status_1': 0,
# 'status_2': 2,
# 'status_3': 2,
# 'status_4': 2,
# 'status_6': 3,
# 'ssid': '...'
# }

# Main function
if __name__ == "__main__":
    run_text = Clock()
    if (not run_text.process()):
        run_text.print_help()
