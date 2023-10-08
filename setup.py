#!/usr/bin/env python

from distutils.core import setup
import os

setup(
    name="pixelperfectpi",
    py_modules=[
        'data/__init__',
        'data/purpleair',
        'data/resolver',
        'di',
        'draw/__init__',
        'draw/drawpanel',
        'draw/multipanelpanel',
        'mqtt',
        'pixelperfectpi',
        'samplebase',
    ],
    scripts=['main.py'],
    data_files=[
        ("fonts", [f"fonts/{x}" for x in os.listdir("fonts")])
    ]
)
