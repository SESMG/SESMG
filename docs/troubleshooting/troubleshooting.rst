Troubleshooting
*************************************************
During execution of the model generator, error messages and associated error messages may occur. 

Contributing to the troubleshooting
===============================

Were you able to solve a bug that was not listed here yet? Help other users and report it by following these simple steps:

1. Open https://github.com/chrklemm/SESMG/edit/master/docs/troubleshooting/troubleshooting.rst

2. Click on the pencil icon in the upper right corner to edit the file.

4. Find the "Installation", or "Modeling" section, depending on what type of error you want to add.

5. Copy the following text block to the end of the respective section and modify the text to describe your error:

Error M-XXX: Error-Name
----------------------------------
**Error Message:** ::

   error message line 1
   error message line 2

**Possible Error Cause:** explain the error cause

**Debugging:** explain how to solve the error
   
6. Click "Create pull request"

7. Name your pull request and click "create pull request".

8. That's it, thanks for your contribution!


Installation
===============================

Error I-001: numpy.generic objects
----------------------------------
**Error Message:** ::

   Cannot interpret attribute 'dtype' of 'numpy.generic' objects' as a data type

**Possible Error Cause:** possible module (e.g., demandlib) not actual

**Debugging:** upgrade module in the installation.cmd (pip install demandlib --upgrade)

Error I-002: port 443
----------------------------------
**Error Message:** ::

   HTTPSConnectionPool(host='pypi.python.org' port=443), due to a timeout

**Possible Error Cause:** A package named in the error message was not installed correctly

**Debugging:** Reinstall the package manually in the virtual environment as follows: 1. open a terminal 2. navigate to your SESMG folder 3. navigate to the scripts-subfolder: ``cd Scripts`` 4. start the virtual environment: ``start /b activate.bat`` 5. install the missing package as follows: ```pip install --default-timeout=100 'PACKAGE-NAME``` (see also `here <https://stackoverflow.com/questions/43298872/how-to-solve-readtimeouterror-httpsconnectionpoolhost-pypi-python-org-port>`_)


Modeling
===============================

General debugging
----------------------------------

Pay attention to the correct spelling:

- Pay attention to correct upper and lower case.
- Do not use spaces in the entire spreadsheet (except for the "comment" columns).
- Make sure that every column of the used lines is filled. Columns that are not used can be filled with a "0".

Make sure that the displayed system can stay in balance. 
- It must always be possible to take off all of the supplied energy and vice versa. 
- The use of excess-sinks and shortage-sources can help to keep the system in balance.

**Your error message is not included? Help us and all users by reporting your error message - with or without a solution!. Thank you!**

.. csv-table:: 
   :file: ../troubleshooting/troubleshooting-modelling.csv
   :header-rows: 1
          

Error M-001: KeyError sequences (sources)
----------------------------------
**Error Message:** ::

   flowsum = source['sequences'].sum() KeyError: 'sequences'

**Possible Error Cause:** A system component was entered incorrectly in the input file.

**Debugging:** For all components  make sure that 1) each column is filled correctly  and 2) the first component of a sheet is entered in the row directly below the header row  and that there are no blank rows between the individual components of a sheet

Error M-002: solver did not exit normally
----------------------------------
**Error Message:** ::

   ApplicationError: Solver (cbc) did not exit normally

**Possible Error Cause:** A system component was entered incorrectly in the input file.

**Debugging:** For all components  make sure that 1) each column is filled correctly  and 2) the first component of a sheet is entered in the row directly below the header row  and that there are no blank rows between the individual components of a sheet


Error M-003: KeyError sequences (results)
----------------------------------
**Error Message:** ::

   df = node_results['sequences'] KeyError: 'sequences'

**Possible Error Cause:** The implemented model probably has an circuit. For example  the excess sink of a bus could achieve higher selling prices than buying from a shortage source. In theory  this could generate an infinitely large profit. Such a model cannot be solved.

**Debugging:** Make sure  there are no circuits within the model.

Error M-004: Memory Error
----------------------------------
**Error Message:** ::

   Memory Error

**Possible Error Cause:** The available memory is not sufficient to solve the model.

**Debugging:** Take the following measures gradually until the error no longer occurs: (1) Restart the used Python interpreter (2) Close unnecessary programs on the computer (3) Make sure that python 64 bit version is used (Python 32 bit can manage only 2 GB of memory). (4)Start the program on a computer with a higher memory.

Error M-005: 
----------------------------------
**Error Message:** ::

   AttributeError: module 'time' has no attribute 'clock'

**Possible Error Cause:** You are using a Python version not compatible with oemof.

**Debugging:** Use Pyhton 3.7.6

Error M-0: 
----------------------------------
**Error Message:** ::

   error message line 1
   error message line 2

**Possible Error Cause:** 

**Debugging:** 

Error M-0: 
----------------------------------
**Error Message:** ::

   error message line 1
   error message line 2

**Possible Error Cause:** 

**Debugging:** 

Error M-0: 
----------------------------------
**Error Message:** ::

   error message line 1
   error message line 2

**Possible Error Cause:** 

**Debugging:** 

Error M-0: 
----------------------------------
**Error Message:** ::

   error message line 1
   error message line 2

**Possible Error Cause:** 

**Debugging:** 

Error M-0: 
----------------------------------
**Error Message:** ::

   error message line 1
   error message line 2

**Possible Error Cause:** 

**Debugging:** 


Error M-023: nearest foot point
----------------------------------
**Error Message:** 
   
   ... get nearest_perp_foot_point foot_point.extend(foot_points[0])
   IndexError: list index out of range

**Possible Error Cause:** The producer could not be connected to the defined heat network. This is probably due to the fact that a right-angled connection to the producer is not possible to the defined pipes.
**Debugging:** Make sure that the producers can be connected to the heat network with a right angle. It is possible that the producer is too far away from the network.


Error M-024: KeyError: 'lon'
----------------------------------
**Error Message:** ::

   ... in get_loc
   raise KeyError(key) from err
   KeyError: 'lon' 

**Possible Error Cause:** No heat source bus has been correctly defined for the heat network.

**Debugging:** make sure the heat source bus has been defined correctly, especially the columns "district heating conn.", "lat", and "lon".


Error M-025: "left_on" OR "left_index"
----------------------------------
**Error Message:** ::

   ... pandas.errors.MergeError: Can only pass argument "left_on" OR "left_index" not both.

**Possible Error Cause:** You are using an incompatible version of the pandas-package.

**Debugging:** Install pandas version 1.0.0 in the virtual environment used for the SESMG


