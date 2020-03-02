@echo Installation started
@echo File path: %~dp0requirements.txt

@echo download the python pip installer
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

@echo install the python pip installer
python get-py.py

@echo download and install required python packages
pip install -r requirements.txt

@echo Installation completed
@pause