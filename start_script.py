import sys
import subprocess
if __name__ == "__main__":
    if sys.platform.startswith("darwin"):
        import program_files.GUI
    else:
        subprocess.call("Scripts/python program_files/GUI.py")
