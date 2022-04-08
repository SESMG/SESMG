Troubleshooting
*************************************************
During execution of the model generator, error messages and associated error messages may occur. 


Contributing to the troubleshooting
===============================

Were you able to solve a bug that was not listed here yet? Help other users and report it by following these simple steps:

1. Open https://github.com/chrklemm/SESMG/tree/master/docs/troubleshooting

2. Open "troubleshooting-installation.csv" or "troubleshooting-modelling.csv", depending on whether your error concerns the installation or the modeling process.

3. Click on the pencil icon in the upper right corner to edit the file.

4. Add a line to the csv file describing your problem. The line consists of three columns "Error Message", "Possible Error Cause" and "Debugging". The columns are separated by commas. Do not use any other commas in your error description.

5. Describe below what you have changed and click "propse changes".

6. Click "Create pull request"

7. Name your pull request and click "create pull request".

8. That's it, thanks for your contribution!



Installation
===============================

Error I-001: numpy.generic objects
----------------------------------
**Error Message:** Cannot interpret attribute 'dtype' of 'numpy.generic' objects' as a data type

**Possible Error Cause:** possible module (e.g., demandlib) not actual

**Debugging:** upgrade module in the installation.cmd (pip install demandlib --upgrade)

Error I-002: port 443
----------------------------------
**Error Message:** HTTPSConnectionPool(host='pypi.python.org' port=443), due to a timeout

**Possible Error Cause:** A package named in the error message was not installed correctly

**Debugging:** Reinstall the package manually in the virtual environment as follows: 1. open a terminal 2. navigate to your SESMG folder 3. navigate to the scripts-subfolder: ``cd Scripts`` 4. start the virtual environment: ``start /b activate.bat`` 5. install the missing package as follows: ```pip install --default-timeout=100 'PACKAGE-NAME``` (see also `here <https://stackoverflow.com/questions/43298872/how-to-solve-readtimeouterror-httpsconnectionpoolhost-pypi-python-org-port>`_)


Error I-XXX: Vorlage
----------------------------------
**Error Message:**
**Possible Error Cause:**
**Debugging:**


Modeling
===============================

**General debugging**:

Pay attention to the correct spelling:

- Pay attention to correct upper and lower case.
- Do not use spaces in the entire spreadsheet (except for the "comment" columns).
- Make sure that every column of the used lines is filled. Columns that are not used can be filled with a "0".

Make sure that the displayed system can stay in balance.
- It must always be possible to take off all of the supplied energy and vice versa.
- The use of excess-sinks and shortage-sources can help to keep the system in balance.

**Your error message is not included? Help us and all users by reporting your error message - with or without a solution!. Thank you!**

Error M-001: KeyError: 'sequences'
----------------------------------
**Error Message:** ... KeyError: 'sequences'

**Possible Error Cause:** 
   - A system component was entered inccorectly in the input file.
   - The implemented model probably has a circuit. For example the excess sink of bus could achieve higher selling prices than buying from a shortage source. In theory this could generate an infinitely large profit. Such a model cannot be solved.  
   - The model may possibly have an over or under supply. This will break the calculation.

**Debugging:** 
   - For all components make sure that 
      1) each column is filled correctly  and 
      2) the first component of a sheet is entered in the row directly below the header row  and that there are no blank rows between the individual components of a sheet
   - Make sure  there are no circuits within the model.
   - The bus of the oversupply or undersupply can be localized by activating excess or shortage.
   
Error M-002: Solver(cbc) did not exit normally
----------------------------------------------
**Error Message:** ApplicationError: Solver (cbc) did not exit normally

**Possible Error Cause:** A system component was entered incorrectly in the input file.

**Debugging:** For all components  make sure that 
   1) each column is filled correctly and 
   2) the first component of a sheet is entered in the row directly below the header row  and that there are no blank rows between the individual components of a sheet
   
Error M-003: Memory Error
---------------------------------------------------
**Error Message:** Memory Error

**Possible Error Cause:** The available memory is not sufficient to solve the model.

**Debugging:** Take the following measures gradually until the error no longer occurs: 
   (1) Restart the used Python interpreter 
   (2) Close unnecessary programs on the computer 
   (3) Make sure that python 64 bit version is used (Python 32 bit can manage only 2 GB of memory). 
   (4)Start the program on a computer with a higher memory.

Error M-004: module 'time' has no attribute 'clock'
---------------------------------------------------
**Error Message:** AttributeError: module 'time' has no attribute 'clock'

**Possible Error Cause:** You are using a Python version not compatible with oemof.

**Debugging:** Use Pyhton 3.7
   
.. csv-table::
   :file: ../troubleshooting/troubleshooting-modelling.csv
   :header-rows: 1
   
   
Upscaling Tool
===============================
.. csv-table:: 
   :file: ../troubleshooting/troubleshooting-upscaling.csv
   :header-rows: 1 
          

