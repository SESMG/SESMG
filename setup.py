#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from setuptools import setup

APP=["start_script.py"]

DATA_FILES = []

OPTIONS = {
    'argv_emulation': True
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"]
)
