=========================================
Spreadsheet Energy System Model Generator
=========================================

The Spreadsheet Energy System Model Generator allows the modeling and 
optimization of energy systems without the need for programming skills. 
The components defined in this spreadsheet are defined with the included Python 
program and the open source Python library “oemof”, assembled to an energy system 
and optimized with the open source solver “cbc”. The modeling results can be 
viewed and analyzed using a browser-based results output.

Installation
-----------------------------------------

**Warning! The installation has only been tested under Windows, using Python 
3.7.6 (64 bit)! Python 3.8 is currently not supported.**


1. Install Python (version 3.5 or higher) 


- **note: Make sure to select "Add pyton to PATH" at the beginning of the Python
installation.**


- go to the `Python download page <https://www.python.org/downloads/>`_
- chose a Python version (e.g., "Python 3.7.6") and click "download"
- download an installer (e.g., "Windows x86-64 executable installer")
- execute the installer on your computer
	

2. Download the Spreadsheet Energy System Model Generator from `GIT <https://git.fh-muenster.de/ck546038/spreadsheet-energy-system-model-generator/-/archive/master/spreadsheet-energy-system-model-generator-master.zip>`_ as .zip folder.


3. Extract the .zip folder into any directory on the computer.


4. Download the CBC-solver from `here <http://ampl.com/dl/open/cbc/cbc-win64.zip>`_


5. Extract the CBC solver into the folder of the Spreadsheet Energy System Model Generator

6. Install "Graphviz"

- go to `Graphviz download page <https://graphviz.gitlab.io/download/>`_ 
- select and download the graphviz version for your device (e.g. `graphviz-2.38.msi for Windows <https://graphviz.gitlab.io/_pages/Download/windows/graphviz-2.38.msi>`_)

- **note: Make sure to select the correct installation location for Graphviz!**

- Execute the installation manager you just downloaded. Choose the following directory for the installation: "C:\\Program Files (x86)\\Graphviz2.38\\" (should be the default settings)

7. Execute the "installation.cmd" file.


- **note: If you receive a "Your computer has been protected by Windows" error message, click "More Information," and then "Run Anyway".**


8. The Spreadsheet Energy System Model Generator has been installed