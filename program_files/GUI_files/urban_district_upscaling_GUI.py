import os
from program_files.urban_district_upscaling\
    .urban_district_upscaling_pre_processing \
    import urban_district_upscaling_pre_processing
from program_files.urban_district_upscaling\
    .urban_district_upscaling_post_processing \
    import urban_district_upscaling_post_processing
from program_files.urban_district_upscaling \
    .urban_district_upscaling_post_processing_clustered \
    import urban_district_upscaling_post_processing_clustered
import subprocess


class UpscalingFrameClass:
    
    @staticmethod
    def scenario_upscaling(pre_scenario, standard_param, scenario_name,
                           clustering):
        # urban_district_upscaling
        urban_district_upscaling_pre_processing(
            pre_scenario=pre_scenario.get(),
            standard_parameter_path=standard_param.get(),
            output_scenario=scenario_name.get(),
            plain_sheet=os.path.join(
                    os.path.dirname(__file__),
                    r'../urban_district_upscaling/plain_scenario.xlsx'),
            clustering=clustering.get())
        
    @staticmethod
    def create_overview(components, clustering):
        if clustering:
            urban_district_upscaling_post_processing_clustered(
                    components.get())
        else:
            urban_district_upscaling_post_processing(components.get())
        subprocess.call(os.path.dirname(__file__) + "/overview.xlsx",
                        shell=True)

    def __init__(self, frame, gui_variables, tk):
        # Headline
        row = 0
        tk.create_heading(frame, 'Urban District Upscaling', 0, row, "w", True,
                          columnspan=7)
        # Description
        row += 1
        tk.create_heading(frame, 'Standardized implementation of '
                          'urban energy systems', 0, row, "w", columnspan=7)
        row += 1
        # Headline
        tk.create_heading(frame, 'Preprocessing', 0, row, "w", True)
        row += 1
        upscaling_elements = {
            'Pre-Scenario':
                [lambda: tk.get_path("xlsx",
                                     gui_variables["pre_scenario_path"]),
                 'Change', "pre_scenario_path"],
            'Standard Parameters':
                [lambda: tk.get_path("xlsx",
                                     gui_variables["standard_parameter_path"]),
                 'Change', "standard_parameter_path"],
            'Scenario Name':
                [lambda: tk.get_path("xlsx", gui_variables["scenario_name"]),
                 'Change', "scenario_name"],
            }
        row = tk.create_button_lines(frame, upscaling_elements, row,
                                     gui_variables)
        tk.create_heading(frame, 'Clustering', 0, row, "w")
        tk.create_checkbox(
                frame,
                gui_variables["clustering"], 1, row)
        row += 1
        upscaling_elements = {
            'Create Scenario':
                [lambda: self.scenario_upscaling(
                       pre_scenario=gui_variables['pre_scenario_path'],
                       standard_param=gui_variables['standard_parameter_path'],
                       scenario_name=gui_variables['scenario_name'],
                       clustering=gui_variables["clustering"]), 'Execute', '']}
        row = tk.create_button_lines(frame, upscaling_elements, row,
                                     gui_variables)
        # Headline
        tk.create_heading(frame, 'Postprocessing', 0, row, "w", True)
        row += 1
        upscaling_elements = {
            'Components CSV for post processing':
                [lambda: tk.get_path("csv", gui_variables["components_path"]),
                 'Change', "components_path"],
            'Create Overview':
                [lambda: self.create_overview(
                        components=gui_variables['components_path'],
                        clustering=True),
                 'Execute', '']}
        tk.create_button_lines(frame, upscaling_elements, row, gui_variables)
