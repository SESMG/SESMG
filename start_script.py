import sys
import subprocess
import os

if __name__ == "__main__":
    if "-c" in sys.argv:
        import program_files.GUI_files.cluster_GUI as cluster_gui
    else:
        if "-s" in sys.argv:
            if sys.platform.startswith("darwin"):
                #import program_files.GUI_files.GUI as GUI
    
                #gui = GUI.GUI()
                subprocess.call("streamlit run {}".format(os.path.dirname(__file__) + "/program_files/GUI_st/GUI_streamlit.py"), shell=True)
                
            
            elif sys.platform.startswith("linux"):
                import program_files.GUI_files.GUI as GUI
    
                gui = GUI.GUI()
            else:
                import program_files.GUI_files.GUI as GUI
    
                gui = GUI.GUI()
                # subprocess.call("Scripts/python program_files/GUI_files/GUI.py")
