import pandas
import os
from program_files.preprocessing import pre_model_analysis


def test_filter_result_component_types():
    """
        Tests if the filtering of the DataFrame via the type column on
        the string component type works correctly.
    """
    test_components_df = pandas.DataFrame.from_dict(
        {"label": ["test1", "test2", "test3"],
         "type": ["sink", "source", "link"]}
    )
    
    return_df = pre_model_analysis.filter_result_component_types(
        components=test_components_df,
        component_type="sink"
    )
    
    pandas.testing.assert_frame_equal(
        left=return_df,
        right=pandas.DataFrame.from_dict(
            {"label": ["test1"],
             "type": ["sink"]}
        )
    )


def test_update_component_investment_decisions():
    """
        Tests if the deactivation of the unused components (here:
        ID_solar_thermal_source) as well as the max. investment
        correction to twice the designed plant size works correctly.
    """
    file_path = os.path.dirname(__file__) \
        + "/test_preprocessing_pre_model_analysis"
    
    return_df, return_list = \
        pre_model_analysis.update_component_investment_decisions(
            components=pandas.read_csv(file_path + "/input_components.csv"),
            model_definition_path=file_path + "/model_definition_example.xlsx",
            model_definition_type_name="sources",
            result_type_name="source",
            investment_boundary_factor=2,
            investment_boundaries=True
        )

    test_sources_df = pandas.read_csv(
        file_path
        + "/output_update_component_investment_decision_factor2.csv",
    ).drop(columns=["Unnamed: 0"])
    
    # Since an entry in this column is a string, without changing the
    # variable type, an error will occur when comparing it with the
    # DataFrame loaded from the CSV file.
    for column in ["Turbine Model", "Modul Model", "Inverter Model"]:
        return_df[column] = return_df[column].astype("str")

    pandas.testing.assert_frame_equal(
        left=return_df,
        right=test_sources_df,
        check_dtype=False
    )
    
    # check whether the list of deactivated components contains
    # "ID_solar_thermal_source"
    assert return_list == ["ID_solar_thermal_source"]


def test_technical_pre_selection():
    from program_files.preprocessing.pre_model_analysis \
        import technical_pre_selection
    pass


def test_tightening_investment_boundaries():
    from program_files.preprocessing.pre_model_analysis \
        import tightening_investment_boundaries
    pass


def test_deactivate_respective_competition_constraints():
    from program_files.preprocessing.pre_model_analysis \
        import deactivate_respective_competition_constraints
    pass


def test_dh_technical_pre_selection():
    from program_files.preprocessing.pre_model_analysis \
        import dh_technical_pre_selection
    pass


def test_bus_technical_pre_selection():
    from program_files.preprocessing.pre_model_analysis \
        import bus_technical_pre_selection
    pass


def test_insulation_technical_pre_selection():
    from program_files.preprocessing.pre_model_analysis \
        import insulation_technical_pre_selection
    pass


def test_update_model_according_pre_model_results():
    from program_files.preprocessing.pre_model_analysis \
        import update_model_according_pre_model_results
    pass
