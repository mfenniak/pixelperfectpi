#!/usr/bin/env python

from distutils.core import setup
import os

setup(
    name="pixelperfectpi",
    py_modules=[
        'component/__init__',
        'component/aqi',
        'component/calendar',
        'component/countdown',
        'component/currenttemp',
        'component/dayofweek',
        'component/distance',
        'component/door',
        'component/media_player',
        'component/oven',
        'component/sunforecast',
        'component/time',
        'component/timer',
        'component/weatherforecast',
        'data/__init__',
        'data/calendar',
        'data/distance',
        'data/door',
        'data/envcanada',
        'data/media_player',
        'data/ovenpower',
        'data/purpleair',
        'data/resolver',
        'data/timer',
        'data/weather_mqtt',
        'data/weather',
        'di',
        'displaybase',
        'draw/__init__',
        'draw/box',
        'draw/drawpanel',
        'draw/multipanelpanel',
        'mqtt',
        'pixelperfectpi',
        'service',
    ],
    scripts=['main.py'],
    data_files=[
        ("fonts", [f"fonts/{x}" for x in os.listdir("fonts")]),
        ("icons", [f"icons/{x}" for x in os.listdir("icons")]),
    ]
)
