#!/usr/bin/env python

from distutils.core import setup
import os

setup(
    name="rpiclock",
    py_modules=['samplebase'],
    scripts=['rpiclock.py'],
    data_files=[
        ("fonts", [f"fonts/{x}" for x in os.listdir("fonts")])
    ]
)
