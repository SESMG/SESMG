Sourcecode documentation
*************************************************
The Spreadsheet Energy System Model Generator has a hierarchical structure and
consists of a total of four work blocks, which in turn consist of various functions and subfunctions.
The individual (sub-)functions are documented with docstrings according to
the PEP 257 standard. Thus, the descriptions of functions, any information about
input and output variables and further details can be easily accessed via the python
help function. The model generator’s flow chart is shown in the following figure, including all
input and output data, used functions and Python libraries.

.. figure:: ../images/program_flow.png
	:width: 100%
	:alt: Program-Flow
	:align: center
	
	Program flow of the Spreadsheet Energy System Model Generator (grey,
	center), as well as local inputs and outputs (bottom) and used Python libraries
	(top).
	
**Create Energy System**. In the first block, the Python library Pandas is used to read
the input xlsx-spreadsheet file. Subsequently, an oemof time index (time steps for a
time horizon with a resolution defined in the input file) is created on the basis of the
parameters imported. This block is the basis for creating the model. The model does
not yet contain any system components, these must be added in the following blocks.

**Create Objects**. In the second block, the system components defined in the xlsxscenario
file are created according to the oemof specifications, and added to the model.
At first, the buses are initialized, followed by the sources, sinks, transformers, storages
and links. With the creation of sources, commodity sources are created first and photovoltaic
sources second. The creation of sinks is divided into six sub-functions, one for
each type of sinks: unfixed sinks, sinks with a given time series, sinks using standard
load profiles (residential heat, commercial heat, electricity) as well as sinks using load
profiles that were created with the Richardson tool. Although it is untypical to convert
a function into a single sub-function, this alternative was chosen for the creation of
transformers and storages. This offers the option to add further sub-functions such as
additional types of transformers and storages lateron. Lastly, the creation of links is
divided into the creation of undirected and directed links.

**Optimize Model**. Within the third block, the CBC solver is utilized to solve the energy
system for minimum costs. It returns the “best” scenario. This block only contains one
function. Again, further functions may be added lateron, for example the combination
of more than one assessment criterion.

**Create Results**. In the last block, the scenario as returned from the CBC solver is
analyzed and prepared for further processing. With the first function of this block, the
results are saved within xlsx-files. It contains ingoing and outgoing energy flows for
every time step of the entire time horizon. With the second function, a set of statistics
for every component is returned into a log-file. Finally, the results are illustrated as
shown in the chapters above.

	
Submodules of program_files
---------------------------

Spreadsheet\_Energy\_System\_Model\_Generator module
-------------------------------------------------------------------

.. automodule:: program_files.Spreadsheet_Energy_System_Model_Generator
   :members:
   :undoc-members:
   :inherited-members:
   :show-inheritance:
   

create\_energy\_system module
--------------------------------------------

.. automodule:: program_files.create_energy_system
   :members:
   :undoc-members:
   :show-inheritance:

create\_objects module
-------------------------------------

.. automodule:: program_files.create_objects
   :members:
   :undoc-members:
   :show-inheritance:
   
create\_graph module
-----------------------------------

.. automodule:: program_files.create_graph
   :members:
   :undoc-members:
   :show-inheritance:

optimize\_model module
-------------------------------------

.. automodule:: program_files.optimize_model
   :members:
   :undoc-members:
   :show-inheritance:
   
create\_results module
-------------------------------------

.. automodule:: program_files.create_results
   :members:
   :undoc-members:
   :show-inheritance:

Interactive\_Results module
-------------------------------------

.. automodule:: program_files.Interactive_Results
   :members:
   :undoc-members:
   :show-inheritance:
           
