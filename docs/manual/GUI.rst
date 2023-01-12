Graphical User Interface
*************************************************

1. Fill in the spreadsheet document according to the instructions in the "Scenario Spreadsheet" chapter.

2. Execute the Run_SESMG_for_**your operating System** file in the main folder.


.. note:: 

	If you receive a "Your computer has been protected by Windows" error message or a similiar one, click "More Information," and then "Run Anyway" (or your operating system specific way to run the programm anyway).

.. figure:: ../images/manual/GUI/GUI.png
   :width: 100 %
   :alt: GUI
   :align: center
   
   The display may vary depending on the operating system. The function "Switch Criteria" is not completely implemented.


Description of the GUI functions

Select the xlsx-scenario to be executed.

**With the result processing parameters one has the possibility to decide,**

	- whether xlsx files should be created or not (1) 
	- whether a console log should be created or not (2)
	- whether the Plotly Dash should be created or not (3)

Now there are three functions for eventing with the scenario choosen:
 1. Displays the currently selected xlsx-scenario as graph.
 2. Modeling and optimization of the selected xlsx-scenario with subsequent output of results.  
 3. Display of the latest optimized scenario (only can be used if an optimization run was done in the current session).
 
The functions under the topic **Results** are used to analyze results older then the current session:
 1. Choose the results directory of the results to be displayed.
 2. Execute the programm to start plotly dash.

 
 .. note::
	The detailed modelling results are also stored within the "results" folder.

Timeseries preperation
======================

Using the timeseries preparation-options, the modeled time system can be reduced so that not all time steps are considered with the modeling. Such a simplification allows shorter runtimes, but may lead to a reduction in the quality of the results [1].

.. warning::

	All time series simplifications can currently only be applied at an output time resolution of hours with 8760 time steps (i.e. one whole year).

GUI Settings
------------

Different possibilities of time series simplification are applicable, for this the following specifications must be deposited in the SESMG GUI:

* **Algorithm**: Indication of the simplification algorithm to be applied.

* **Index**: Algorithm specific configuration.

* **Criterion**: Criterion according to which cluster algorithms are applied.

* **Period**: Time periods which are clustered together (weeks, days, hours)

* **Season**: Time periods within which clustering takes place (year, seasons, months)


Pre-Modeling
------------

If this function is activated, the model is split into two model-runs. In a temporally simplified pre-model, potentially irrelevant investment decisions are identified and removed from the main model run ("technical pre-selection", see [1]). Optionally, the investment boundaries for the investment decisions remaining in the model can be adjusted with the freely selectable _investment_boundary_factor_ ("tightening of technical boundaries", see [1]). The pre-run and main run are automatically executed one after the other.

Available Algorithms
--------------------

The following algorithms are applicable and must be specified with the following additional information:

.. csv-table::
	:file: ../manual/timeseries_preparation.csv
	:header-rows: 1

k-means / k-medoids
^^^^^^^^^^^^^^^^^^^^^
"The k-clustering algorithm divides a time series into a given number k of clusters so that the squared deviation of the cluster centers of gravity is minimal. The procedure is well described by Green et al. [2]. k-means-clustering as well as k-medoids-clustering are carried out using the python libraries ``scikit-learn'', respectively ``scikit-learn-extra''." [1] Different cluster criteria (1. temperature, 2. solar radiation, 3. electricity demand) as well as different periods (days and weeks) can be applied. To apply the criterion "electricity demand", a column "el_demand_sum" must be inserted in the scenario.xlsx file in the weather-data sheet, which defines the reference consumption.

averaging
^^^^^^^^^^^^^^^^^^^^^
"In averaging, successive time periods (e.g. two consecutive days) are averaged and combined into one segment" [1]. Values of different numbers of days and weeks can be applied.

slicing A/B
^^^^^^^^^^^^^^^^^^^^^
"In slicing every $n$-th period is selected, e.g. every second day, and subsequently recombined to a reduced time series." [1] Slicing A: every n-th period is **selected and considered** within the modeling. Slicing B: every n-th period is **deleted and removed** from the modeling.

downsampling A/B
^^^^^^^^^^^^^^^^^^^^^
"The temporal resolution of an entire time series is changed. For example, the resolution can be changed from a 1-hourly to a 3-hourly temporal resolution." [1] "On the one hand it allows the *consideration* of every $n$-th hour [downsampling A]. Thereby the number of modeled time steps must be at least halved ($n$=2). To allow a smaller time series reduction, the possibility to *remove* every $n$-th hour was also implemented [downsampling B]" [1].

heuristic selection
^^^^^^^^^^^^^^^^^^^^^
"In heuristic selection, representative time periods of a time series are selected from certain selection criteria" [1] "Based on the approach of Poncelet et al. heuristic selection scheme[s are] carried out" [1]

Available selection schemes:

+--------+---------+-------------------------------+--------------+------------------+---------------------+
| index  | period  | criterion                     | temperature  | solar radiation  | electricity demand  |
+========+=========+===============================+==============+==================+=====================+
| 1      | 2       | year                          | hp, lv       | --               | --                  |
+--------+---------+-------------------------------+--------------+------------------+---------------------+
| 2      | 4       | year                          | hp, lv       | ha, la           | --                  |
+--------+---------+-------------------------------+--------------+------------------+---------------------+
| 3      | 8       | summer, winter                | hp, lv       | ha, la           | --                  |
+--------+---------+-------------------------------+--------------+------------------+---------------------+
| 4      | 16      | winter, spring, summer, fall  | hp, lv       | ha, la           | --                  |
+--------+---------+-------------------------------+--------------+------------------+---------------------+
| 5      | 24      | winter, spring, summer, fall  | hp, lv       | ha, la           | ha, la              |
+--------+---------+-------------------------------+--------------+------------------+---------------------+

Acronyms: hp=highest peak, lv=lowest valley, ha=highest average, la=lowest average


Further schemes can be added here: https://github.com/chrklemm/SESMG/blob/master/program_files/technical_data/hierarchical_selection_schemes.xlsx


random sampling
^^^^^^^^^^^^^^^^^^^^^
"In random sampling, a predetermined number of random periods (e.g. days or weeks) are selected and used as representatives." [1] "The python library ``random'' is utilized. To ensure reproducability, a ``seed'' is defined, so that with each run the same random periods will be selected. Furthermore, a random time series of e.g. 10 periods thereby automatically makes up 10 periods of a random time series of, e.g. 20 periods" [1]


Further Adjustments
-------------------

Depending on the simplification applied, further adjustments to the energy system must be made automatically.

**Adjustment of time series of non-divisible length:**
"For a time series' adjustments, the simplification factor should ideally be divisible by the length of the given time series without remainder. For example, out of 365 days, every fifth day can be selected via slicing without any problems (365/5=73), but every tenth day results in a remainder (365/10=36.5). In order to be able to simplify the time series correctly, in such cases the given time series is shortened so far that the calculation is correct. For slicing with every tenth day, for example, the time series would be shortened to 360 days (360/10=36). In sampling methods, the selected periods are strung together and merged into a new time series. The individual sample periods are partially assigned new time stamps" [1].

**Variable cost factor:**
"To ensure the correct consideration of the relationship between variable and periodical (annual) costs in the case of shortened time series, variable costs are multiplied by the variable cost factor" [1]:

`variable cost factor = original number of timesteps / new number of timesteps`



References
==========
[1] Klemm C. *Model-based run-time and memory optimization for a mixed-use multi-energy system model with high spatial resolution*, preprint submitted to 'Applied Energy', `Available here <https://www.researchgate.net/publication/361634152_Model-based_run-time_and_memory_optimization_for_a_mixed-use_multi-energy_system_model_with_high_spatial_resolution>`_ , 2022.

[2] Green, Richard, Iain Staffell, and Nicholas Vasilakos. *Divide and Conquer? k-Means Clustering of Demand Data Allows Rapid and Accurate Simulations of the British Electricity System.* IEEE Transactions on Engineering Management 61.2 (2014): 251-260.
