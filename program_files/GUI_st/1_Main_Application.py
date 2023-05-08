"""
    Jan N. Tockloth - jan.tockloth@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Janik Budde - janik.budde@fh-muenster.de
"""
import sys
import os
from datetime import datetime
from streamlit.components.v1 import html
import streamlit as st


# Setting new system path to be able to refer to parent directories
parent = os.path.abspath('.')
sys.path.insert(1, parent)

from program_files.GUI_st.GUI_st_global_functions import \
    clear_GUI_main_settings, safe_GUI_input_values, \
    import_GUI_input_values_json, st_settings_global, run_SESMG, \
    read_markdown_document, create_simplification_index, \
    create_cluster_simplification_index, load_result_folder_list
from program_files.preprocessing.pareto_optimization import run_pareto

# settings the initial streamlit page settings
st_settings_global()

# opening the input value dict, which will be saved as a json
GUI_main_dict = {}

# Import the saved GUI settings from the last session
settings_cache_dict_reload = import_GUI_input_values_json(
    os.path.dirname(__file__) + "/GUI_st_cache.json")

# Import GUI help comments from the comment json and safe as a dict
GUI_helper = import_GUI_input_values_json(
    os.path.dirname(__file__) + "/GUI_st_help_comments.json")


def nav_page(page_name, timeout_secs=3) -> None:
    """
        Javascript used to switch between to Streamlit pages
        automatically.

        :param page_name: string containing the pages name possible \
            entries are: Result_Processing, Urban_District_Upscaling, ...
        :type page_name: str
        :param timeout_secs: seconds until system returns timeout
        :type timeout_secs: float
    """
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].href.toLowerCase().endsWith("/"
                        + page_name.toLowerCase())) {
                        links[i].click();
                        return;
                    }
                }
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {
                    setTimeout(attempt_nav_page, 100, page_name,
                               start_time, timeout_secs);
                } else {
                    alert("Unable to navigate to page '" + page_name
                          + "' after " + timeout_secs + " second(s).");
                }
            }
            window.addEventListener("load", function() {
                attempt_nav_page("%s", new Date(), %d);
            });
        </script>
    """ % (page_name, timeout_secs)
    html(nav_script)


def main_start_page() -> None:
    """
        Definition of the start page for the GUI with introducing texts.
    """

    reduced_readme = read_markdown_document(
        "README.md", f'{"docs/images/readme/*"}')

    # Display any remaining lines in the readme using the st.markdown() \
    # function
    st.markdown(''.join(reduced_readme), unsafe_allow_html=True)


def main_input_sidebar() -> st.runtime.uploaded_file_manager.UploadedFile:
    """
        Function building the sidebar of the main application including
        all input options and starting the processes.

        :return: - **model_definition_input_sheet_path** \
            (st.runtime.uploaded_file_manager.UploadedFile) - model \
            defintion as a st.UploadedFile
    """
    # Creating Frame as st.form_submit_button
    with st.sidebar.form("Input Parameters"):

        if "state_submitted_optimization" not in st.session_state:
            st.session_state["state_submitted_optimization"] = "not done"

        # Submit button to start optimization.
        st.form_submit_button(
            label="Start Optimization",
            on_click=change_state_submitted_optimization,
            help=GUI_helper["main_fs_start_optimization"])

        # Functions to upload the model definition sheet file.
        # Header
        st.title("Upload Model Definition")

        # fileuploader for the model definition
        model_definition_input = st.file_uploader(
            label="Upload your model definition sheet.",
            help=GUI_helper["main_fu_model_definition"])

        # Header
        st.title("Input Parameters")

        # creating three tabs inside the sidebar
        tab_bar = st.tabs(["Preprocessing", "Processing", "Postprocessing"])

        # create tab 2 for Preprocessing
        with tab_bar[0]:
            # Functions to input the preprocessing parameters

            # Functions to input the parameters for timeseries preparation.
            # Dict of choosable algorithms matching the streamlit input
            # index for \
            # selectbox's preselections
            timeseries_algorithm_dict = {"None": 0,
                                         "k_means": 1,
                                         "k_medoids": 2,
                                         "averaging": 3,
                                         "slicing A": 4,
                                         "slicing B": 5,
                                         "downsampling A": 6,
                                         "downsampling B": 7,
                                         "heuristic selection": 8,
                                         "random sampling": 9}

            # Timeseries Index Range None or 1 to 365
            timeseries_index_range_list = ["None"] + list(range(1, 366))

            # Dict of choosable clustering crtieria matching the streamlit \
            # input index for selectbox's preselections
            timeseries_cluster_criteria_dict = {"None": 0,
                                                "temperature": 1,
                                                "dhi": 2,
                                                "el_demand_sum": 3,
                                                "heat_demand_sum": 4}

            # Dict of choosable timeseries periods matching the streamlit \
            # input index for selectbox's preselections
            input_timeseries_period_dict = {"None": 0,
                                            "hours": 1,
                                            "days": 2,
                                            "weeks": 3}

            # Dict of choosable timeseries periods matching the streamlit \
            # input index for selectbox's preselections
            input_timeseries_season_dict = {"None": 0,
                                            4: 1,
                                            12: 2}

            # Timeseries preparation input inside an expander.
            with st.expander(label="Timeseries Simplification"):
                # Choosing timeseries parameters - algorithm
                GUI_main_dict["input_timeseries_algorithm"] = \
                    st.selectbox(
                        label="Algorithm",
                        options=timeseries_algorithm_dict.keys(),
                        index=settings_cache_dict_reload[
                            "input_timeseries_algorithm_index"],
                        help=GUI_helper["main_dd_timeser_algorithm"])

                # Choosing timeseries parameters - index
                GUI_main_dict["input_timeseries_cluster_index"] = \
                    st.selectbox(
                        label="Index",
                        options=timeseries_index_range_list,
                        index=settings_cache_dict_reload[
                            "input_timeseries_cluster_index_index"],
                        help=GUI_helper["main_dd_timeser_cluster_index"])
                # Choosing timeseries parameters - cluster criterion
                GUI_main_dict["input_timeseries_criterion"] = \
                    st.selectbox(
                        label="Cluster Criterion",
                        options=timeseries_cluster_criteria_dict.keys(),
                        index=settings_cache_dict_reload[
                            "input_timeseries_criterion_index"],
                        help=GUI_helper[
                            "main_dd_timeser_cluster_criterion"])
                # Choosing timeseries parameters - period
                GUI_main_dict["input_timeseries_period"] = \
                    st.selectbox(
                        label="Period",
                        options=input_timeseries_period_dict.keys(),
                        index=settings_cache_dict_reload[
                            "input_timeseries_period_index"],
                        help=GUI_helper["main_dd_timeser_period"])
                # Choosing timeseries parameters - season
                GUI_main_dict["input_timeseries_season"] = \
                    st.selectbox(
                        label="Season",
                        options=input_timeseries_season_dict.keys(),
                        index=settings_cache_dict_reload[
                            "input_timeseries_season_index"],
                        help=GUI_helper["main_dd_timeser_season"])

            # transform input values of Timeseries Simplification to an index
            # which will be safed in the GUI cache to be able to reload
            # setting. Needs to be an index for st.selectboxes.
            # create list for transformation from simplification input to
            # index values
            simpification_index_list = [
                ["input_timeseries_algorithm_index",
                 timeseries_algorithm_dict,
                 "input_timeseries_algorithm"],
                ["input_timeseries_criterion_index",
                 timeseries_cluster_criteria_dict,
                 "input_timeseries_criterion"],
                ["input_timeseries_period_index",
                 input_timeseries_period_dict,
                 "input_timeseries_period"],
                ["input_timeseries_season_index",
                 input_timeseries_season_dict,
                 "input_timeseries_season"]]

            # transform to index values and safe in the GUI_main_dict
            create_simplification_index(input_list=simpification_index_list,
                                        input_output_dict=GUI_main_dict)

            # transform input_timeseries_cluster_index seperately
            create_cluster_simplification_index(
                input_value="input_timeseries_cluster_index",
                input_output_dict=GUI_main_dict,
                input_value_index="input_timeseries_cluster_index_index")

            # Pre-Model setting and pre-model timeseries preparation input
            # inside an expander.
            with st.expander("Pre-Modeling Settings"):

                # Checkbox to activate the pre-modeling
                GUI_main_dict["input_activate_premodeling"] = \
                    st.checkbox(
                        label="Activate Pre-Modeling",
                        value=settings_cache_dict_reload[
                            "input_activate_premodeling"],
                        help=GUI_helper["main_cb_prem_active"])

                # Activate functions to reduce the maximum design capacity
                GUI_main_dict["input_premodeling_invest_boundaries"] = \
                    st.checkbox(
                        label="Investment Boundaries Tightening",
                        value=settings_cache_dict_reload[
                            "input_premodeling_invest_boundaries"],
                        help=GUI_helper["main_cb_thightening_active"])
                # Slider to set the tightening factor for maximum design
                # capacity
                GUI_main_dict["input_premodeling_tightening_factor"] = \
                    st.slider(
                        label="Investment Tightening Factor",
                        min_value=1,
                        max_value=100,
                        value=settings_cache_dict_reload[
                            "input_premodeling_tightening_factor"],
                        help=GUI_helper["main_sl_tightening_factor"])

                # Choosing pre-model timeseries parameters - algorithm
                GUI_main_dict["input_premodeling_timeseries_algorithm"] = \
                    st.selectbox(
                        label="Algorithm (Pre-Model)",
                        options=timeseries_algorithm_dict.keys(),
                        index=settings_cache_dict_reload[
                            "input_premodeling_timeseries_algorithm_index"],
                        help=GUI_helper["main_dd_prem_timeser_algorithm"])
                # Choosing pre-model timeseries parameters - index
                GUI_main_dict["input_premodeling_timeseries_cluster_index"] = \
                    st.selectbox(
                        label="Index (Pre-Model)",
                        options=timeseries_index_range_list,
                        index=settings_cache_dict_reload[
                            "input_premodeling_timeseries_cluster_index_index"],
                        help=GUI_helper[
                            "main_dd_prem_timeser_cluster_index"])
                # Choosing pre-model timeseries parameters - cluster criterion
                GUI_main_dict["input_premodeling_timeseries_criterion"] = \
                    st.selectbox(
                        label="Cluster Criterion (Pre-Model)",
                        options=timeseries_cluster_criteria_dict.keys(),
                        index=settings_cache_dict_reload[
                            "input_premodeling_timeseries_criterion_index"],
                        help=GUI_helper[
                            "main_dd_prem_timeser_cluster_criterion"])
                # Choosing pre-model timeseries parameters - period
                GUI_main_dict["input_premodeling_timeseries_period"] = \
                    st.selectbox(
                        label="Period (Pre-Model)",
                        options=input_timeseries_period_dict.keys(),
                        index=settings_cache_dict_reload[
                            "input_premodeling_timeseries_period_index"],
                        help=GUI_helper["main_dd_prem_timeser_period"])
                # Choosing pre-model timeseries parameters - season
                GUI_main_dict["input_premodeling_timeseries_season"] = \
                    st.selectbox(
                        label="Season (Pre-Model)",
                        options=input_timeseries_season_dict.keys(),
                        index=settings_cache_dict_reload[
                            "input_premodeling_timeseries_season_index"],
                        help=GUI_helper["main_dd_prem_timeser_season"])

            # transform input values of Timeseries Simplification to an
            # index which will be safed in the GUI cache to be able to
            # reload setting. Needs to be an index for st.selectboxes.
            # create list for transformation from premodel
            # simplification input to index values
            simpification_premodel_index_list = [
                ["input_premodeling_timeseries_algorithm_index",
                 timeseries_algorithm_dict,
                 "input_premodeling_timeseries_algorithm"],
                ["input_premodeling_timeseries_criterion_index",
                 timeseries_cluster_criteria_dict,
                 "input_premodeling_timeseries_criterion"],
                ["input_premodeling_timeseries_period_index",
                 input_timeseries_period_dict,
                 "input_premodeling_timeseries_period"],
                ["input_premodeling_timeseries_season_index",
                 input_timeseries_season_dict,
                 "input_premodeling_timeseries_season"]]

            # transform to index values and safe in the GUI_main_dict
            create_simplification_index(
                input_list=simpification_premodel_index_list,
                input_output_dict=GUI_main_dict)

            # transform input_timeseries_cluster_index seperately
            create_cluster_simplification_index(
                input_value="input_premodeling_timeseries_cluster_index",
                input_output_dict=GUI_main_dict,
                input_value_index="input_premodeling_timeseries_cluster_index_index")

            # Elements to set the pareto points.
            with st.expander("Multi-Objective Optimization"):
                # Multiselect element
                input_pareto_points = st.multiselect(
                    label="Pareto Points",
                    options=list(range(1, 100)),
                    default=settings_cache_dict_reload[
                        "input_pareto_points"],
                    help=GUI_helper["main_ms_pareto_points"])
                # sort pareto points as required to run sesmg
                if input_pareto_points is not None:
                    input_pareto_points.sort(reverse=True)

                GUI_main_dict["input_pareto_points"] = input_pareto_points

            # Function to upload the distrct heating precalulation inside an \
            # expander.
            with st.expander("Advanced District Heating Precalculation"):
                # Checkboxes modeling when using district heating clustering.
                GUI_main_dict["input_cluster_dh"] = \
                    st.checkbox(
                        label="Clustering District Heating Network",
                        value=settings_cache_dict_reload[
                            "input_cluster_dh"],
                        help=GUI_helper["main_cb_cluster_dh"])

                # Checkboxes to activate dh precalc.
                GUI_main_dict["input_activate_dh_precalc"] = st.checkbox(
                        label="Activate District Heating Precalculations",
                        value=settings_cache_dict_reload[
                            "input_activate_dh_precalc"],
                        help=GUI_helper["main_cb_activate_dh_precalc"])

                # read sub folders in the result folder directory un wich \
                # the preresults are stored
                existing_result_foldernames_list = load_result_folder_list()
                # create select box with the folder names which are in the \
                # results folder
                existing_result_folder = st.selectbox(
                    label="Choose a district heating precalculation folder",
                    options=existing_result_foldernames_list,
                    help=GUI_helper["main_dd_result_folder"],
                    index=settings_cache_dict_reload[
                        "input_dh_folder_index"])

                # set variable as the list index to save in cache
                GUI_main_dict["input_dh_folder_index"] = \
                    existing_result_foldernames_list.index(
                    existing_result_folder)

                # set the path to dh precalc if active or not
                if GUI_main_dict["input_activate_dh_precalc"]:
                    # create path to precalc folder
                    GUI_main_dict["input_dh_folder"] = \
                        os.path.join(os.path.dirname(os.path.dirname(
                                        os.path.dirname(
                                            os.path.abspath(__file__)))),
                                     "results",
                                     existing_result_folder)
                else:
                    GUI_main_dict["input_dh_folder"] = ""

            # create criterion switch
            GUI_main_dict["input_criterion_switch"] = \
                st.checkbox(
                    label="Switch Criteria",
                    value=settings_cache_dict_reload["input_criterion_switch"],
                    help=GUI_helper["main_cb_criterion_switch"])

        # create tab 2 for processing
        with tab_bar[1]:
            # Slider number of threads
            GUI_main_dict["input_num_threads"] = st.slider(
                label="Number of threads",
                min_value=1,
                max_value=35,
                help=GUI_helper["main_sl_number_threats"],
                value=settings_cache_dict_reload["input_num_threads"])

            # indexing the chosen solver of the cache session as an inputvalue
            # for st. selectbox
            # Dict of choosable solvers the streamlit input index for
            # selectbox preselections
            input_solver_dict = {"cbc": 0,
                                 "gurobi": 1}
            # chosing the solver in an select box
            GUI_main_dict["input_solver"] = st.selectbox(
                label="Optimization Solver",
                options=input_solver_dict.keys(),
                index=settings_cache_dict_reload["input_solver_index"],
                help=GUI_helper["main_sb_solver"])

            # preparing input_timeseries_season for GUI cache as an streamlit \
            # input index
            GUI_main_dict["input_solver_index"] = \
                input_solver_dict[GUI_main_dict["input_solver"]]

        # create tab 2 for postprocessing
        with tab_bar[2]:
            # Input Postprocessing Parameters
            # Functions to input the postprocessing parameters.

            # Input result processing parameters
            GUI_main_dict["input_xlsx_results"] = \
                st.checkbox(
                    label="Create xlsx-files",
                    value=settings_cache_dict_reload["input_xlsx_results"],
                    help=GUI_helper["main_cb_xlsx_results"])

            GUI_main_dict["input_console_results"] = \
                st.checkbox(
                    label="Create console-log",
                    value=settings_cache_dict_reload["input_console_results"],
                    help=GUI_helper["main_cb_console_results"])

    return model_definition_input


def main_error_definition() -> None:
    """
        Raises an streamlit internal error if model run is started
        without an uploaded model definition
    """
    # raise an error advice
    st.error(body=GUI_helper["main_error_defintion"], icon="🚨")

    # reset session state
    st.session_state["state_submitted_optimization"] = "not done"


def main_clear_cache_sidebar() -> None:
    """
        Creating the for submit button to clear the GUI cache
    """

    # creating sidebar form submit structure
    with st.sidebar.form("Clear Cache"):
        # set initial session state for clear cache submit button
        if "state_submitted_clear_cache" not in st.session_state:
            st.session_state["state_submitted_clear_cache"] = "not done"

        # create submit button
        st.form_submit_button(
            label="Clear all GUI Settings",
            on_click=change_state_submitted_clear_cache,
            help=GUI_helper["main_fs_clear_cache"])

    # Clear all GUI settings if clear latest result paths clicked
    if st.session_state["state_submitted_clear_cache"] == "done":
        # create and safe dict, set paths empty
        clear_GUI_main_settings(json_file_path=os.path.dirname(__file__)
                                + "/GUI_st_cache.json")
        # reset session state for clear cache
        st.session_state["state_submitted_clear_cache"] = "not done"
        # rerun whole script to update GUI settings
        st.experimental_rerun()


def create_result_paths() -> None:
    """
        Create result paths and result folder. Set session.states

    """
    # Setting the path where to safe the modeling results
    res_folder_path = os.path.join(os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))), 'results')
    GUI_main_dict["res_path"] = res_folder_path \
        + '/' \
        + model_definition_input_file.name.split("/")[-1][:-5] \
        + datetime.now().strftime('_%Y-%m-%d--%H-%M-%S')
    os.mkdir(GUI_main_dict["res_path"])
    GUI_main_dict["premodeling_res_path"] = \
        GUI_main_dict["res_path"] + "/pre_model_results"

    # safe path as session state for the result processing page
    st.session_state["state_result_path"] = GUI_main_dict["res_path"]
    st.session_state["state_premodeling_res_path"] = \
        GUI_main_dict["premodeling_res_path"]


def save_run_settings() -> None:
    """
        Function to safe the GUI setting in the result folder and reset
        session state.
    """
    # save GUI settings in result folder
    safe_GUI_input_values(
        input_values_dict=GUI_main_dict,
        json_file_path=st.session_state["state_result_path"]
        + "/GUI_st_run_settings.json")

    # reset session state
    st.session_state["state_submitted_optimization"] = "not done"


def change_state_submitted_optimization() -> None:
    """
        Setup session state for the optimization form-submit as an
        change event as on-click to switch the state.
    """
    st.session_state["state_submitted_optimization"] = "done"


def change_state_submitted_clear_cache() -> None:
    """
        Setup session state for the clear_cache form-submit as an
        change event as on-click to switch the state.
    """
    st.session_state["state_submitted_clear_cache"] = "done"
    st.session_state["state_submitted_optimization"] = "not done"


# staring sidebar elements as standing elements
model_definition_input_file = main_input_sidebar()
main_clear_cache_sidebar()

# load the start page if modell run is not submitted
if st.session_state["state_submitted_optimization"] == "not done":
    main_start_page()

# starting process is modell run is  submitted
if st.session_state["state_submitted_optimization"] == "done":

    # raise error if run is started without uploading a model definition
    if not model_definition_input_file:

        # load error messsage
        main_error_definition()

    elif model_definition_input_file != "":

        # safe the GUI_main_dice as a chache for the next session
        safe_GUI_input_values(input_values_dict=GUI_main_dict,
                              json_file_path=os.path.dirname(__file__)
                              + "/GUI_st_cache.json")

        # create spinner info text
        st.info(GUI_helper["main_info_spinner"], icon="ℹ️")

        # Starting the model run
        if len(GUI_main_dict["input_pareto_points"]) == 0:

            # function to create the result pasths and store session state
            create_result_paths()

            with st.spinner("Modeling in Progress..."):

                # start model run
                run_SESMG(GUI_main_dict=GUI_main_dict,
                          model_definition=model_definition_input_file,
                          save_path=GUI_main_dict["res_path"])

                # save GUI settings in result folder and reset session state
                save_run_settings()

            # switch page after the model run completed
            nav_page(page_name="Result_Processing", timeout_secs=3)

        # Starting a pareto modeul rum
        elif len(GUI_main_dict["input_pareto_points"]) != 0:

            with st.spinner("Modeling in Progress..."):

                # run_pareto retuns res path
                GUI_main_dict["res_path"] = \
                    run_pareto(
                        limits=[i / 100 for i in
                                GUI_main_dict["input_pareto_points"]],
                        model_definition=model_definition_input_file,
                        GUI_main_dict=GUI_main_dict)

                # safe path as session state for the result processing page
                st.session_state["state_result_path"] = \
                    GUI_main_dict["res_path"]

                # save GUI settings in result folder and reset session state
                save_run_settings()

            # switch page after the model run completed
            nav_page(page_name="Result_Processing", timeout_secs=3)
