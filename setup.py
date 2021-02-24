#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8"),
    ) as fh:
        return fh.read()

setup(
    name="SESMG",
    version="0.1.1",
    license="MIT",
    author="Christian Klemm",
    author_email="christian.klemm@fh-muenster.de",
    classifiers=[
        # complete classifier list:
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
            ],

    install_requires=[
        "pandas==0.24.2",
        "numpy==1.16.6",
        "tables==3.5.2",
        "openpyxl==3.0.0",
        "oemof.solph==0.4",
        "oemof.thermal==0.0.3",
        "demandlib==0.1.6",
        "pvlib==0.7.1",
        "feedinlib==0.0.12",
        "richardsonpy==0.2.1",
        "dash==1.7.0",
        "dash_canvas==0.1.0",
        "pydot==1.4.1",
        "graphviz==0.13.2",
        "xlrd==1.2.0",
        "Pyomo==5.7.1"
        ],
    extras_require={
        "dev": ["pytest", "sphinx", "sphinx_rtd_theme"],
    },  
)

