import sys
import subprocess
if __name__ == "__main__":
    if "-c" in sys.argv:
        import program_files.GUI_files.cluster_GUI as cluster_gui
    else:
        if sys.platform.startswith("darwin"):
            import program_files.GUI_files.GUI as GUI
            gui = GUI.GUI()
        elif sys.platform.startswith("linux"):
            import program_files.GUI_files.GUI as GUI
            gui = GUI.GUI()
        else:
            import program_files.GUI_files.GUI as GUI
            gui = GUI.GUI()
            #subprocess.call("Scripts/python program_files/GUI_files/GUI.py")
