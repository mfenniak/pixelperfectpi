#!/usr/bin/env python

from distutils.core import setup
import os

setup(
    name="pixelperfectpi",
    py_modules=['mqtt', 'samplebase', 'pixelperfectpi', 'di', 'data/purpleair', 'data/resolver', 'data/__init__'],
    scripts=['main.py'],
    data_files=[
        ("fonts", [f"fonts/{x}" for x in os.listdir("fonts")])
    ]
)
