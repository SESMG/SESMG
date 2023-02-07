import pandas


def create_building_insulation(building: dict, sheets: dict,
                               standard_parameters: pandas.ExcelFile) -> dict:
    """
        In this method, the U-value potentials as well as the building
        year-dependent U-value of the insulation types are obtained from
        the standard parameters to create the insulation components in
        the scenario.
    
        :param building: dictionary holding the building specific data
        :type building: dict
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import append_component

    yoc_roof = building["year of construction roof"]
    yoc_wall = building["year of construction wall"]
    yoc_window = building["year of construction windows"]
    roof = building["rooftype"]
    yoc_component = [yoc_roof, yoc_wall, yoc_window]
    yoc_component_new = [yoc_component[i] if yoc_component[i] > 1918
                         else "<1918" for i in range(len(yoc_component))]
    building_component = ["roof", "outer wall", "window"]

    standard_param = standard_parameters.parse("7_insulation")
    standard_param.set_index("year of construction", inplace=True)

    u_values = {}

    for yoc, comp in zip(yoc_component_new, building_component):
        u_values.update(
            {
                comp: [
                    standard_param.loc[yoc][comp],
                    standard_param.loc["potential"][comp],
                    standard_param.loc["periodical costs"][comp],
                    standard_param.loc["periodical constraint costs"][comp],
                ]
            }
        )
        if comp == "roof":
            u_values[comp] += [
                standard_param.loc["potential flat"]["roof"],
                standard_param.loc["periodical costs flat"]["roof"],
                standard_param.loc["periodical constraint costs flat"]["roof"],
            ]
    param_dict = {
        "active": 1,
        "sink": str(building["label"]) + "_heat_demand",
        "temperature indoor": 20,
        "heat limit temperature": 15,
    }
    if building["area windows"]:
        window_dict = param_dict.copy()
        window_dict.update(
            {
                "label": str(building["label"]) + "_window",
                "U-value old": u_values["window"][0],
                "U-value new": u_values["window"][1],
                "area": building["area windows"],
                "periodical costs": u_values["window"][2],
                "periodical constraint costs": u_values["window"][3],
            }
        )
        sheets = append_component(sheets, "insulation", window_dict)

    if building["area outer wall"]:
        wall_dict = param_dict.copy()
        wall_dict.update(
            {
                "label": str(building["label"]) + "_wall",
                "U-value old": u_values["outer wall"][0],
                "U-value new": u_values["outer wall"][1],
                "area": building["area outer wall"],
                "periodical costs": u_values["outer wall"][2],
                "periodical constraint costs": u_values["outer wall"][3],
            }
        )
        sheets = append_component(sheets, "insulation", wall_dict)

    if building["area roof"]:
        u_value_new = u_values["roof"][4 if roof == "flat roof" else 1]
        periodical_costs = u_values["roof"][5 if roof == "flat roof" else 2]
        periodical_constr = u_values["roof"][3 if roof != "flat roof" else 6]
        roof_dict = param_dict.copy()
        roof_dict.update(
            {
                "label": str(building["label"]) + "_roof",
                "U-value old": u_values["roof"][0],
                "U-value new": u_value_new,
                "area": building["area roof"],
                "periodical costs": periodical_costs,
                "periodical constraint costs": periodical_constr,
            }
        )
        sheets = append_component(sheets, "insulation", roof_dict)

    return sheets
