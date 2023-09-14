#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics, font_path
import time
import requests


class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        # print("font_path", font_path)
        font.LoadFont(font_path + "/7x13.bdf")
        textColor = graphics.Color(255, 255, 0)
        pos = offscreen_canvas.width
        my_text = self.args.text

        resp = requests.get('http://10.156.95.135/json')
        if resp.status_code == 200:
            purpleair = resp.json()
            print("purpleair", repr(purpleair))
        else:
            print("purpleair", resp.status_code)

        while True:
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, my_text)
            pos -= 1
            if (pos + len < 0):
                pos = offscreen_canvas.width

            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

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
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()


