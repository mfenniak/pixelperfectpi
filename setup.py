#!/usr/bin/env python

from distutils.core import setup
import os

setup(
    name="pixelperfectpi",
    py_modules=['samplebase', 'mqtt'],
    scripts=['pixelperfectpi.py'],
    data_files=[
        ("fonts", [f"fonts/{x}" for x in os.listdir("fonts")])
    ]
)
