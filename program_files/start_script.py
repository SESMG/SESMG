from program_files.GUI_st import GUI_st_global_functions
import sys
from streamlit.web import cli as stcli

from pathlib import Path

if __name__ == '__main__':
    # Setting new system path to be able to refer to parent directories
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = Path(sys._MEIPASS)
    else:
        bundle_dir = Path(__file__).parent.parent
    sys.argv = ["streamlit", "run", str(bundle_dir) + "/program_files/GUI_st/1_Main_Application.py",
                "--global.developmentMode=false"]
    sys.exit(stcli.main())
