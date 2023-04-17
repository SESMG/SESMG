# Spreadsheet Energy System Model Generator (SESMG) 
[![Generic badge](https://img.shields.io/badge/content-what/why-darkgreen.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)
[![Generic badge](https://img.shields.io/badge/content-how-green.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)


[![codecov](https://codecov.io/gh/SESMG/SESMG/branch/master/graph/badge.svg?token=70AHZEB2IN)](https://codecov.io/gh/SESMG/SESMG)
[![Test Coverage](https://api.codeclimate.com/v1/badges/5ab50cca9d852028f3df/test_coverage)](https://codeclimate.com/github/SESMG/SESMG/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/5ab50cca9d852028f3df/maintainability)](https://codeclimate.com/github/SESMG/SESMG/maintainability)
[![Documentation Status](https://readthedocs.org/projects/spreadsheet-energy-system-model-generator/badge/?version=latest)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/?badge=latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Software Description

The **SESMG** is an energy system model generator with the focus on the optimization of urban energy systems, which can, however, also be used for the modeling of other types of energy systems. The **SESMG** is based on the 'Open Energy Modelling Framework' (oemof) and comes, compared to other modeling tools with advantages regarding user-friendliness, as
 
 * the model definition is based on spreadsheets, therefore no programming skills are required for the entire modeling process,
 * urban energy system models with any size can automatically conceptualized,
 * visualization of complex results are automatically created in the form of system graphs, Pareto-fronts, energy amounts, capacity diagrams, and many more, as well as
 * a set of standard (but still customizable) parameters are given, including detailed descriptions and references.
 
Furthermore, the **SESMG** comes with important modeling methods, enabling holistic modeling of spatially high resolution modeling of mixed-use multi energy systems, such as
 
 * considering the multi-energy system (MES) approach
 * applying multi-objective optimization by using the epsilon-constraint-method, as well as
 * providing several methods for model-based reduction of computational requirements (run-time and RAM).

![workflow_graph_SESMG](/docs/images/readme/workflow_graph.png)

## Quick Start 
[![Generic badge](https://img.shields.io/badge/content-how-green.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)

#### Please note: 
A detailed description of the installation process for Windows, MacOS and Linux can be found in the [documentation (chapter installation)](
https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/02.01.00_installation.html). The Quick Start installation guide is only recommended for advanced users or users with programming experience!

### Step 1) Download Python 3.7 or newer (Python 3.10 was not tested yet)

- go to the Python download page
- chose a Python version (e.g. “Python 3.7.6”) and click “download”
- download the operating system specific installer (e.g. “Windows x86-64 executable installer”)
- execute the installer on your computer

### Step 2) Download the Spreadsheet Energy System Model Generator from `GitHub <https://github.com/SESMG/SESMG>`_ as .zip folder and extract the .zip folder into any directory on the computer. 

### Step 3) Install pip (Linux only)

run `$ sudo apt-get install python3-pip`

### Step 4) Download the CBC-solver (Windows and Linux only) 

#### For Windows:

Download [here](http://ampl.com/dl/open/cbc/cbc-win64.zip)

<u>Within this step there are two options: </u>
- install the cbc-Solver on your whole operating system 
- copy and paste the downloaded executable two your **SESMG**-working directory

#### For Linux:

run `$ sudo apt-get install coinor-cbc`

### Step 5) Install Graphviz (Windows and Linux only) 

#### For Windows:
Download [here](https://graphviz.gitlab.io/download/)

- select and download the graphviz version for your device (e.g. graphviz-2.38.msi for Windows)
- Execute the installation manager you just downloaded. Choose the following directory for the installation: “C:\Program Files (x86)\Graphviz2.38" (should be the default settings)

#### For Linux:

run `$ sudo apt-get install graphviz`

### Step 6) Install libpq-dev to avoid a psycopg2 error (Linux only)

run `$ sudo apt-get install libpq-dev`

### Step 7) Start the operating system specific installation file. 


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

The Spreadsheet Energy System Model Generator was carried out within the research project [R2Q "Resource Planing for Urban Districts](https://www.fh-muenster.de/forschungskooperationen/r2q/index.php). The project was funded by the Federal Ministry of Education and Research (BMBF) funding program [RES:Z "Resource-Efficient Urban Districts](https://ressourceneffiziente-stadtquartiere.de). The funding measure is part of the flagship initiative "City of the Future" within the BMBF's framework programme "Research for Sustainable Development - FONA3". The contributors gratefully acknowledge the support of BMBF (grant number 033W102).

### License

This project is published under GNU GPL-3.0 license, click [here](https://github.com/chrklemm/SESMG/blob/master/LICENSE) for more details.

## Contributing 
[![Generic badge](https://img.shields.io/badge/content-contribution-blue.svg)](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/#)


Issues and Pull Requests are greatly appreciated. If you've never contributed to an open source project before I'm more than happy to walk you through how to create a pull request.

Detailed description of the contribution procedure as well as the projects coding standards can be found [here](/docs/CONTRIBUTING.md).
