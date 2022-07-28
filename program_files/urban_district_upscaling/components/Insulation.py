def create_building_insulation(building, sheets, standard_parameters):
    """
        In this method, the U-value potentials as well as the building
        year-dependent U-value of the insulation types are obtained from
        the standard parameters to create the insulation components in
        the scenario.

        :param building:
        :type building:
        :param sheets:
        :type sheets:
        :param standard_parameters:
        :type standard_parameters:
    """
    from program_files import append_component
    
    yoc = building["year of construction"]
    roof = building["rooftype"]
    
    standard_param = standard_parameters.parse('insulation')
    standard_param.set_index("year of construction", inplace=True)
    if int(yoc) <= 1918:  # TODO
        yoc = "<1918"
    u_values = {}
    for comp in ["roof", "outer wall", "window"]:
        u_values.update(
            {comp: [standard_param.loc[yoc][comp],
                    standard_param.loc["potential"][comp],
                    standard_param.loc["periodical costs"][comp],
                    standard_param.loc["periodical constraint costs"][comp]]})
        if comp == "roof":
            u_values[comp] \
             += [standard_param.loc["potential flat"]["roof"],
                 standard_param.loc["periodical costs flat"]["roof"],
                 standard_param.loc["periodical constraint costs flat"]["roof"]
                 ]
    param_dict = {'comment': 'automatically_created',
                  'active': 1,
                  'sink': str(building["label"]) + "_heat_demand",
                  'temperature indoor': 20,
                  'heat limit temperature': 15}
    if building["windows"]:
        window_dict = param_dict.copy()
        window_dict.update(
            {'label': str(building["label"]) + "_window",
             'U-value old': u_values["window"][0],
             'U-value new': u_values["window"][1],
             'area': building["windows"],
             'periodical costs': u_values["window"][2],
             'periodical constraint costs': u_values["window"][3]})
        sheets = append_component(sheets, "insulation", window_dict)

    if building["walls_wo_windows"]:
        wall_dict = param_dict.copy()
        wall_dict.update(
            {'label': str(building["label"]) + "_wall",
             'U-value old': u_values["outer wall"][0],
             'U-value new': u_values["outer wall"][1],
             'area': building["walls_wo_windows"],
             'periodical costs': u_values["outer wall"][2],
             'periodical constraint costs': u_values["outer wall"][3]})
        sheets = append_component(sheets, "insulation", wall_dict)

    if building["roof area"]:
        u_value_new = u_values["roof"][4 if roof == "flat roof" else 1]
        periodical_costs = u_values["roof"][5 if roof == "flat roof" else 2]
        periodical_constr = u_values["roof"][3 if roof != "flat roof" else 6]
        roof_dict = param_dict.copy()
        roof_dict.update(
            {'label': str(building["label"]) + "_roof",
             'U-value old': u_values["roof"][0],
             'U-value new': u_value_new,
             'area': building["roof area"],
             'periodical costs': periodical_costs,
             'periodical constraint costs': periodical_constr})
        sheets = append_component(sheets, "insulation", roof_dict)
        
    return sheets
