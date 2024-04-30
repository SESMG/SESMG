"""
    Gregor Becker - gregor.becker@fh-muenster.de
    Jan N. Tockloth - jan.tockloth@fh-muenster.de
"""

import os
import sys
import streamlit.web.bootstrap

from streamlit import config as _config


def start_streamlit() -> None:
    """
    This function initializes and starts a Streamlit application in headless \
    mode.

    This function sets up the Streamlit configuration options for headless \
    mode, disables development mode and XSRF protection, and then runs the \
    Streamlit application.
    """
    # Change the current working directory to the directory of this script
    os.chdir(os.path.dirname(__file__))

    # Configure Streamlit options
    _config.set_option("server.headless", True)
    _config.set_option("global.developmentMode", False)
    _config.set_option("server.enableXsrfProtection", False)

    # Show the Streamlit configuration
    _config.show_config()

    # Import and run the Streamlit application

    streamlit.web.bootstrap.run(str(sys._MEIPASS) +
                                "/program_files/GUI_st/1_Main_Application.py",
                                '',
                                [],
<<<<<<< HEAD
                                {})
=======
                                {})
>>>>>>> master
