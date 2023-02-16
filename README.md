# Spreadsheet Energy System Model Generator (SESMG) 
[![Generic badge](https://img.shields.io/badge/content-what/why-darkgreen.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)
[![Generic badge](https://img.shields.io/badge/content-how-green.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)


[![codecov](https://codecov.io/gh/SESMG/SESMG/branch/master/graph/badge.svg?token=70AHZEB2IN)](https://codecov.io/gh/SESMG/SESMG)
[![Test Coverage](https://api.codeclimate.com/v1/badges/5ab50cca9d852028f3df/test_coverage)](https://codeclimate.com/github/SESMG/SESMG/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/5ab50cca9d852028f3df/maintainability)](https://codeclimate.com/github/SESMG/SESMG/maintainability)
[![Documentation Status](https://readthedocs.org/projects/spreadsheet-energy-system-model-generator/badge/?version=latest)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/?badge=latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Software Description

The **SESMG** provides a spreadsheet interface to the Open Energy Modeling Framework (oemof), allowing modeling and optimization of urban energy systems based a spreadsheet.

**SESMG** makes it easier to create oemof-based energy system models.

- You don't need to touch the command line
- You don't need programming skills
- **SESMG** is an intuitive spreadsheet driven tool

The components defined in this spreadsheet are defined with the included Python 
program and the open source Python library “oemof”, assembled to an energy system 
and optimized with open source solvers, e.g. “cbc”. The modeling results can be 
viewed and analyzed using a browser-based results output.)

![workflow_graph_SESMG](/docs/images/readme/workflow_graph.jpeg)

## Quick Start 
[![Generic badge](https://img.shields.io/badge/content-how-green.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)

### Step 1) Download Python 3.7 or newer (Python 3.10 was not tested yet)

- go to the Python download page
- chose a Python version (e.g. “Python 3.7.6”) and click “download”
- download the operating system specific installer (e.g. “Windows x86-64 executable installer”)
- execute the installer on your computer

Linux only: 
- run `$ sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2`
- test by running `$ python3 --version`

### Step 2) Download the Spreadsheet Energy System Model Generator from GIT as .zip folder 

### Step 3) Extract the .zip folder into any directory on the computer
Watch out: we do not support spaces in the path yet. It will lead to an error if there is one.

### Step 4) Install pip (Linux only)

run `$ sudo apt-get install python3-pip`

### Step 5) Install tkinter (Linux only)

run `$ sudo apt-get install python3.7-tk`

### Step 6) Download the CBC-solver (Windows and Linux only) 

#### For Windows:

Download [here](http://ampl.com/dl/open/cbc/cbc-win64.zip)

<u>Within this step there are two options: </u>
- install the cbc-Solver on your whole operating system 
- copy and paste the downloaded executable two your **SESMG**-working directory

#### For Linux:

run `$ sudo apt-get install coinor-cbc`

### Step 7) Install Graphviz (Windows and Linux only) 

#### For Windows:
Download [here](https://graphviz.gitlab.io/download/)

- select and download the graphviz version for your device (e.g. graphviz-2.38.msi for Windows)
- Execute the installation manager you just downloaded. Choose the following directory for the installation: “C:\Program Files (x86)\Graphviz2.38" (should be the default settings)

#### For Linux:

run `$ sudo apt-get install graphviz`

### Step 8) Start the operating system specific installation file. 


## SESMG Features & Releases 
[![Generic badge](https://img.shields.io/badge/content-what/why-darkgreen.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)

### Examples
Examples are stored in a separate GIT-Repository: https://github.com/chrklemm/SESMG_Examples

### Project status
✓ Draft (alpha, beta) State <br />
✓ Modeling and Optimization of holistic energy systems <br />
✓ Automated modeling of urban energy systems <br /> 
✓ Several result plotting oportunities <br />
✓ Usable on Windows, MacOS and Linux <br />

✘ More time to code other things ... wait ✓!  

## Detailed Documentation! 
[![Generic badge](https://img.shields.io/badge/content-references-orange.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)

The [documentation](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/),
which includes detailed instructions for **installation** and **use**, **troubleshooting** 
and much more, can be accessed via the following link:

https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/

## Questions? 
[![Generic badge](https://img.shields.io/badge/content-who-yellow.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)
[![Generic badge](https://img.shields.io/badge/content-references-orange.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)

[Use the Discussions Section](https://github.com/chrklemm/SESMG/discussions) and let's chat!

## Credits 
[![Generic badge](https://img.shields.io/badge/content-who-yellow.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)


### Contact and Code of Conduct 

Code of Conduct can be found [here](/CODE_OF_CONDUCT.md).

#### Contact information 
Münster University of Applied Sciences

Christian Klemm - christian.klemm@fh-muenster.de

### Acknowledgments

The Spreadsheet Energy System Model Generator was carried out within the 
research project [R2Q "Resource Planing for Urban Districts](https://www.fh-muenster.de/forschungskooperationen/r2q/index.php). 
The project was funded by the Federal Ministry 
of Education and Research (BMBF) funding program [RES:Z "Resource-Efficient Urban Districts](https://ressourceneffiziente-stadtquartiere.de). The funding measure is part of the flagship initiative "City of the Future" within the BMBF's framework programme "Research for Sustainable Development - FONA3".
The contributors gratefully acknowledge the support of BMBF (grant number 033W102).

### License

This project is published under GNU GPL-3.0 license, click [here](https://github.com/chrklemm/SESMG/blob/master/LICENSE) for more details.

## Contributing 
[![Generic badge](https://img.shields.io/badge/content-contribution-blue.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)


Issues and Pull Requests are greatly appreciated. If you've never contributed to an open source project before I'm more than happy to walk you through how to create a pull request.

Detailed description of the contribution procedure as well as the projects coding standards can be found [here](/docs/CONTRIBUTING.md).
