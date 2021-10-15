Troubleshooting
*************************************************
During execution of the model generator, error messages and associated error messages may occur. 


**General debugging**:

Pay attention to the correct spelling:

- Pay attention to correct upper and lower case.
- Do not use spaces in the entire spreadsheet (except for the "comment" columns).
- Make sure that every column of the used lines is filled. Columns that are not used can be filled with a "0".

Make sure that the displayed system can stay in balance. 
- It must always be possible to take off all of the supplied energy and vice versa. 
- The use of excess-sinks and shortage-sources can help to keep the system in balance.


**Your error message is not included? Help us and all users by reporting your error message - with or without a solution!. Thank you!**

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
.. csv-table:: 
   :file: ../troubleshooting/troubleshooting-installation.csv
   :header-rows: 1


Modeling
===============================
.. csv-table:: 
   :file: ../troubleshooting/troubleshooting-modelling.csv
   :header-rows: 1
   
   
Upscaling Tool
===============================
.. csv-table:: 
   :file: ../troubleshooting/troubleshooting-upscaling.csv
   :header-rows: 1 
          

