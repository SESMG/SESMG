Troubleshooting
*************************************************
During execution of the model generator, error messages and associated program aborts may occur. 

**General debugging**:

Pay attention to the correct spelling:

- Pay attention to correct upper and lower case.
- Do not use spaces in the entire spreadsheet (except for the "comment" columns).
- Make sure that every column of the used lines is filled. Columns that are not used can be filled with an "x".

Make sure that the displayed system can stay in balance. 
- It must always be possible to take off all of the supplied energy and vice versa. 
- The use of excess-sinks and shortage-sources can help to keep the system in balance.


**Known error messages**:

.. warning:: 

	flowsum = source['sequences'].sum()
	
	KeyError: 'sequences'
	
or

.. warning:: 

	ApplicationError: Solver (cbc) did not exit normally

- **Possible Error Cause**: A system component was entered incorrectly in the input file. 
- **Debugging**: For all components, make sure that 1) each column is filled correctly, and 2) the first component of a sheet is entered in the row directly below the header row, and that there are no blank rows between the individual components of a sheet


.. warning::

    df = node_results['sequences']
    
    KeyError: 'sequences'
    
- **Possible Error Cause**: The implemented model probably has an circuit. For example, the excess sink of a bus could achieve higher selling prices than buying from a shortage source. In theory, this could generate an infinitely large profit. Such a model cannot be solved.
- **Debugging**: Make sure, there are no circuits within the model.



.. warning:: 

	Memory Error
	
- **Possible Error Cause**: The available memory is not sufficient to solve the model.
- **Debugging**: Take the following measures gradually until the error no longer occurs:

	- Restart the used Python interpreter
	- Close unnecessary programs on the computer
	- Make sure that  python 64 bit version is used (Python 32 bit can manage only 2 GB of memory).
	- Start the program on a more powerful computer.

.. warning:: 

	AttributeError: module 'time' has no attribute 'clock'

- **Possible Error Cause**: You are using a Python version not compatible with oemof.
- **Debugging**: Use Pyhton 3.7

.. warning:: 

	ValueError: operands could not be broadcast together with shapes (8784,) (8760,) 

- **Possible Error Cause**: The weather dataset contains the wrong number of data points for using feedinlib.
- **Debugging**: Make sure that the number of weather data points corresponds to the time steps of the model (At hourly resolution, one year has 8760 time steps). When simulating a leap year, it is recommended limiting the time horizon to 8760 hours.

.. warning:: 

	ValueError: pyutilib.common._exceptions.ApplicationError: Solver (cbc) did not exit normally
	
- **Possible Error Cause**: A value for the use of the investment module (e.g., "min Investment Capacity") was not filled in.
- **Debugging**: Make sure, that all necessary cells of the spreadsheet have been filled in.

.. warning::

	KeyError: '*__any component name__*'
	
- **Possible Error Cause**: Incorrectly assigned bus name for the input or output of a component
- **Debugging**: Check that all bus references are correct. Also check for typos.

.. warning::
	
	TypeError: ufunc 'true_divide' not supported for the input types, and the inputs could not be safely 
	coerced to any supported types according to the casting rule ''safe''
	
- **Possible Error Cause**: The column "annual demand" was not filled in correctly for a sink. 
- **Debugging**: Make sure to use the "annual demand" column for SLP and Richardson sinks and the "nominal value" column for time series sinks.

.. warning::

	AttributeError: 'str' object has no attribute 'is_variable_type'
	
- **Possible Error Cause**: The cost value for an activated excess sink or shortage source was not correctly specified in the bus sheet
- **Debugging**: Make sure that all excess/sortage prices consist of real numbers. Also check for typos.

.. warning::

	"exe.cmd" is not executed (no errror messages)
	
- **Possible Error Cause**: The used Python environment does not work correctly.
- **Debugging**: Reinstall python (see "Getting Started", step 1 "Install Python").


Your error message is not included? Do not hesitate to contact the developers.
