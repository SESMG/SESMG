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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9'],

    install_requires=[
        "oemof.solph>=0.4",
        "openpyxl>=3.0.0",
        "oemof.thermal>=0.0.5",
        "open_fred-cli>=0.0.1",
        "basemap>=1.3.0",
        "richardsonpy>=0.2.0",
        "graphviz>=0.20",
        "scikit-learn-extra>=0.2.0",
        "memory-profiler>=0.60.0",
        "dhnx>=0.0.2",
        "sympy>=1.10.0",
        "osmnx>=1.2.0",
        "xlsxwriter>=3.0.0",
        "seaborn>=0.11.0",
        "dash>=2.4.0",
        "dash_canvas>=0.1.0"
        ],
    dependency_links = [
     "git+https://github.com/oemof/feedinlib.git@refs/pull/73/head",
     "git+https://github.com/oemof/demandlib.git@refs/pull/51/head"
    ],
    extras_require={
        "dev":
            ["pytest", "sphinx", "sphinx_rtd_theme"]
    },  
)

