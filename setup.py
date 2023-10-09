#!/usr/bin/env python

from distutils.core import setup
import os

setup(
    name="pixelperfectpi",
    py_modules=[
        'component/__init__',
        'component/aqi',
        'component/calendar',
        'component/currenttemp',
        'component/dayofweek',
        'component/oven',
        'component/sunforecast',
        'component/time',
        'component/weatherforecast',
        'data/__init__',
        'data/calendar',
        'data/envcanada',
        'data/overpower',
        'data/purpleair',
        'data/resolver',
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
        ("fonts", [f"fonts/{x}" for x in os.listdir("fonts")])
    ]
)
