#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import setuptools
import re
import glob

__version__ = "0.5.0"
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

OPTIONS = {
    'argv_emulation': True,
    'includes': ["streamlit"]
}

setuptools.setup(
    name="SESMG",
    version=__version__,
    license="GPL-3.0-only",
    author="Christian Klemm",
    author_email="christian.klemm@fh-muenster.de",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #packages=setuptools.find_packages(),
    #requires=install_requires,
    app=["start_script.py"],
    data_files=[('program_files', glob.glob('program_files/*.*'))],
    options={'py2app': OPTIONS},
    setup_requires=["py2app"],
    classifiers=[
        # complete classifier list:
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    extras_require={"dev": ["pytest", "sphinx", "sphinx_rtd_theme"]},
)
