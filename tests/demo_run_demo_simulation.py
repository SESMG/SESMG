def run_demo_simulation(demo_file: str, demo_results: str, mode: str, solver: str, session_state: dict, sesmg_main_func) -> None:
    """
    Executes the optimization algorithm in a testable way.

    :param demo_file: path to the model definition file
    :param demo_results: path to the demo result folder
    :param mode: optimization mode ("monetary" or "emissions")
    :param solver: selected solver ("cbc" or "gurobi")
    :param session_state: dictionary simulating Streamlit session state
    :param sesmg_main_func: injected main function to run the optimization
    """
    criterion_switch = (mode == "emissions")

    sesmg_main_func(
        model_definition_file=demo_file,
        result_path=demo_results,
        num_threads=1,
        timeseries_prep=["None", "None", "None", "None", 0],
        graph=False,
        criterion_switch=criterion_switch,
        xlsx_results=False,
        console_results=False,
        solver=solver,
        cluster_dh=False,
        district_heating_path=""
    )

    session_state["state_submitted_demo_run"] = "not done"
