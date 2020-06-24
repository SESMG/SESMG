@echo ################################
@echo Installation started
@echo File path: %~dp0program_files
@echo ################################

@echo #################################
@echo download the python pip installer
@echo #################################

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

@echo ################################
@echo install the python pip installer
@echo ################################

python get-py.py

@echo #############################################
@echo download and install required python packages
@echo #############################################

pip install pandas==0.25.3
pip install numpy==1.17.4
pip install tables==3.5.2
pip install openpyxl==3.0.0

pip install oemof==0.3.2
pip install demandlib==0.1.6
pip install pvlib==0.7.1
pip install feedinlib==0.0.12
pip install richardsonpy==0.2.1
pip install dash==1.7.0
pip install dash_canvas==0.1.0
pip install pydot==1.4.1
pip install graphviz==0.13.2


@echo ######################
@echo Installation completed
@echo ######################

@pause