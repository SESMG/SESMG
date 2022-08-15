#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import setuptools
import re

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()
    
with open("test/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

setuptools.setup(
    name="SESMG",
    version=version,
    license="GPL-3.0-only",
    author="Christian Klemm",
    author_email="christian.klemm@fh-muenster.de",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7"],
    extras_require={
        "dev":
            ["pytest", "sphinx", "sphinx_rtd_theme"]
    },  
)





