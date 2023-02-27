import os
from program_files import urban_district_upscaling_pre_processing
from program_files.urban_district_upscaling.urban_district_upscaling_post_processing import (
    urban_district_upscaling_post_processing,
)
from program_files.urban_district_upscaling.urban_district_upscaling_post_processing_clustered import (
    urban_district_upscaling_post_processing_clustered,
)
import subprocess


class UpscalingFrameClass:
    """
    This class is used to create the Graphical User Interface
    (GUI) for the Urban_District_Upscaling_Tool.
    In this context, it uses the methods of the superclass
    MethodsGUI.

    :param frame: tkinter upscaling frame
    :type frame: ttk.Frame
    :param gui_variables: dictionary containing GUI variables
    :type gui_variables: dict
    :param tk: object containing the super class methods
    :type tk: GUI object

    """

    @staticmethod
    def scenario_upscaling(
        pre_scenario, standard_param, scenario_name, clustering, clustering_dh
    ):
        """
        Methods starting the upscaling pre_processing Algorithm

        :param pre_scenario: containing path to pre_scenario file
        :type pre_scenario: tk.StringVar
        :param standard_param: containing path to standard_parameter
            file
        :type standard_param: tk.StringVar
        :param scenario_name: containing path to scenario_name file
        :type scenario_name: tk.StringVar
        :param clustering: containing boolean rather the pre
            scenario is clustered or not
        :type clustering: tk.BooleanVar
        :param clustering_dh:
        :type clustering_dh:
        """
        urban_district_upscaling_pre_processing(
            paths=[
                pre_scenario.get(),
                standard_param.get(),
                scenario_name.get(),
                os.path.join(
                    os.path.dirname(__file__),
                    r"../urban_district_upscaling/plain_scenario.xlsx",
                ),
            ],
            clustering=clustering.get(),
            clustering_dh=clustering_dh.get(),
        )

    @staticmethod
    def create_overview(us_input, components, building_or_cluster, result_path):
        """
        Methods starting the upscaling post_processing Algorithm

        :param components: containing path to components.csv
        :type components: tk.StringVar
        :param clustering: containing boolean rather the pre
            scenario is clustered or not
        :type clustering: tk.BooleanVar

        """
        # if clustering:
        #    urban_district_upscaling_post_processing_clustered(components.get())
        # else:
        #    urban_district_upscaling_post_processing(components.get())
        # subprocess.call(os.path.dirname(__file__) + "/overview.xlsx", shell=True)

        from program_files.postprocessing import building_specific_results

        building_specific_results.create_building_specific_results(
            us_sheet_raw_data=us_input.get(),
            components_raw_data=components.get(),
            building_or_cluster=building_or_cluster.get(),
            result_path=result_path.get(),
        )

    def __init__(self, frame, gui_variables, tk):
        # Headline
        row = 0
        tk.create_heading(
            frame, "Urban District Upscaling", 0, row, "w", True, columnspan=7
        )
        # Description
        row += 1
        tk.create_heading(
            frame,
            "Standardized implementation of " "urban energy systems",
            0,
            row,
            "w",
            columnspan=7,
        )
        row += 1
        # Headline
        tk.create_heading(frame, "Preprocessing", 0, row, "w", True)
        row += 1
        upscaling_elements = {
            "Pre-Scenario": [
                lambda: tk.get_path("xlsx", gui_variables["pre_scenario_path"]),
                "Change",
                "pre_scenario_path",
            ],
            "Standard Parameters": [
                lambda: tk.get_path("xlsx", gui_variables["standard_parameter_path"]),
                "Change",
                "standard_parameter_path",
            ],
            "Scenario Name": [
                lambda: tk.get_path("xlsx", gui_variables["scenario_name"]),
                "Change",
                "scenario_name",
            ],
        }
        row = tk.create_button_lines(frame, upscaling_elements, row, gui_variables)
        row = (
            tk.create_cb_lines(frame, {"Clustering": "clustering"}, row, gui_variables)
            + 1
        )
        row = (
            tk.create_cb_lines(
                frame, {"Clustering DH": "clustering_dh"}, row, gui_variables
            )
            + 1
        )
        upscaling_elements = {
            "Create Scenario": [
                lambda: self.scenario_upscaling(
                    pre_scenario=gui_variables["pre_scenario_path"],
                    standard_param=gui_variables["standard_parameter_path"],
                    scenario_name=gui_variables["scenario_name"],
                    clustering=gui_variables["clustering"],
                    clustering_dh=gui_variables["clustering_dh"],
                ),
                "Execute",
                "",
            ]
        }
        row = tk.create_button_lines(frame, upscaling_elements, row, gui_variables)
        # Headline
        tk.create_heading(frame, "Postprocessing", 0, row, "w", True)
        row += 1
        tk.create_option_menu(
            frame, gui_variables["building_or_cluster"], ["building", "cluster"], 1, row
        )
        row += 1
        upscaling_elements = {
            "Components CSV for post processing": [
                lambda: tk.get_path("csv", gui_variables["components_path"]),
                "Change",
                "components_path",
            ],
            "Result Path": [
                lambda: tk.get_path("folder", gui_variables["result_path"]),
                "Change",
                "result_path",
            ],
            "Create Overview": [
                lambda: self.create_overview(
                    us_input=gui_variables["pre_scenario_path"],
                    components=gui_variables["components_path"],
                    building_or_cluster=gui_variables["building_or_cluster"],
                    result_path=gui_variables["result_path"],
                ),
                "Execute",
                "",
            ],
        }
        tk.create_button_lines(frame, upscaling_elements, row, gui_variables)
