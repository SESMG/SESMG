Installation
*************************************************

.. warning:: 

	Warning! The installation has only been tested using Python 3.7.6 (64 bit)! Python 3.8 is currently not supported.

Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Install Python (version 3.5 or higher) 


.. note:: 

	Make sure to select "Add pyton to PATH" at the beginning of the Python installation.


- go to the `Python download page <https://www.python.org/downloads/>`_
- chose a Python version (e.g., "Python 3.7.6") and click "download"
- download an installer (e.g., "Windows x86-64 executable installer")
- execute the installer on your computer
	

2. Download the Spreadsheet Energy System Model Generator from `GIT <https://github.com/chrklemm/SESMG/archive/SESMG-v0.0.6.zip>`_ as .zip folder.


3. Extract the .zip folder into any directory on the computer.

4. Download the CBC-solver from `here <http://ampl.com/dl/open/cbc/cbc-win64.zip>`_


5. Extract the CBC solver into the folder of the Spreadsheet Energy System Model Generator

6. Install "Graphviz"

- go to `Graphviz download page <https://graphviz.gitlab.io/download/>`_ 
- select and download the graphviz version for your device (e.g. `graphviz-2.38.msi for Windows <https://graphviz.gitlab.io/_pages/Download/windows/graphviz-2.38.msi>`_)

.. note:: 

	Make sure to select the correct installation location for Graphviz!!

- Execute the installation manager you just downloaded. Choose the following directory for the installation: "C:\\Program Files (x86)\\Graphviz2.38\\" (should be the default settings)

7. Execute the "Windows_installation.cmd" file.


.. note:: 

	If you receive a "Your computer has been protected by Windows" error message, click "More Information," and then "Run Anyway".


8. The Spreadsheet Energy System Model Generator has been installed.

MacOS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Install Python (version 3.5 or higher) 


.. note:: 

	Make sure to select "Add pyton to PATH" at the beginning of the Python installation.


- go to the `Python download page <https://www.python.org/downloads/>`_
- chose a Python version (e.g., "Python 3.7.6") and click "download"
- download an installer (e.g., "Python 3.7.6 macOS 64-bit installer")
- execute the installer on your computer
	

2. Download the Spreadsheet Energy System Model Generator from `GIT <https://github.com/chrklemm/SESMG/archive/SESMG-v0.0.6.zip>`_ as .zip folder.


3. Extract the .zip folder into any directory on the computer.

4. Excecute the "MacOS_installation.command" file.

5. The Spreadsheet Energy System Model Generator has been installed.

Linux 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. Install Python (version 3.5 or higher)

- go to `<https://phoenixnap.com/kb/how-to-install-python-3-ubuntu/>`_
- use Python3.7 instead of Python3.8
.. note:: 
	
	Make sure that the alias python3 is set to Python3.7.x.
	If not use update-alternatives to change it.
	 
2. Download the Spreadsheet Energy System Model Generator from `GIT <https://github.com/chrklemm/SESMG/archive/SESMG-v0.0.6.zip>`_ as .zip folder.

3. Extract the .zip folder into any directory on the computer.

4. Install PIP 

``$ sudo apt-get install python3-pip``

5. Install tkinter 

``$ sudo apt-get install python3.7-tk``
	
6. Install Graphviz

``$ sudo apt-get install graphviz``
	
7. Install the CBC-Solver 

``$ sudo apt-get install coinor-cbc``
	
8. Execute the "Linux_installtion.sh" file.

9. The Spreadsheet Energy System Model Generator has been installed.
 
