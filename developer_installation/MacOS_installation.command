#!/bin/bash
function exists_in_list() {
	# mask the user given inputs
    LIST=$1
    DELIMITER=$2
    VALUE=$3
	# replace delimiter by whitespaces
    LIST_WHITESPACES=`echo $LIST | tr "$DELIMITER" " "`
	# iterate threw the list to check for given Version 
    for x in $LIST_WHITESPACES; do
        if [ "$x" = "$VALUE" ]; then
			# return 0 if version was found
            return 0
        fi
    done
	# return 1 if version was not found
    return 1
}

echo --------------------------------
echo Building the Virtual Enviroment
echo File path: "$(dirname "$0")"
echo --------------------------------
cd "$(dirname "$0")"
cd ..

echo "Enter your Python Version here:"
read PYVERSION

list_of_allowed_versions="3.8,3.9,3.10,3.11"

if exists_in_list "$list_of_allowed_versions" "," $PYVERSION; then
    echo "Version Input allowed, installation will continue."
else
    echo "Input not in the list of allowed Versions restart the installation with an allowed version." 1>&2 
	exit 1 
fi

python$PYVERSION -m venv venv
source venv/bin/activate

echo ---------------------------------------------
echo download and install required python packages
echo ---------------------------------------------

brew install cbc
brew install geos
brew install graphviz
brew install postgresql

venv/bin/pip3 install -r requirements.txt

echo ----------------------
echo Installation completed
echo Starting SESMG
echo ----------------------

venv/bin/python$PYVERSION -m streamlit run "program_files/GUI_st/1_Main_Application.py"
osascript -e 'tell application "Terminal" to quit'
