import importlib.util
import sys
from pathlib import Path

file_path = Path(__file__).parents[1] / "program_files/GUI_st/pages/3_Result_Processing.py"
spec = importlib.util.spec_from_file_location("result_processing_loaded", str(file_path))
result_processing_loaded = importlib.util.module_from_spec(spec)
sys.modules["result_processing_loaded"] = result_processing_loaded
spec.loader.exec_module(result_processing_loaded)