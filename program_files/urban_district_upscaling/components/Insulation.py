def create_building_insulation(building_id: str, yoc: int, areas: list,
                               roof_type: str, standard_parameters):
    """
        In this method, the U-value potentials as well as the building
        year-dependent U-value of the insulation types are obtained from
        the standard parameters to create the insulation components in
        the scenario.

        :param building_id: building label
        :type building_id: str
        :param yoc: year of construction of the given building
        :type yoc: int
        :param areas: list containing window area [0] wall area [1] \
            and roof area [2]:
        :type areas: list
        :param roof_type: defines rather the roof is a flat one or not
        :type roof_type: str
        :param standard_parameters:
        :type standard_parameters:
    """
    from program_files import append_component
    insul_standard_param = standard_parameters.parse('insulation')
    insul_standard_param.set_index("year of construction", inplace=True)
    if int(yoc) <= 1918:  # TODO
        yoc = "<1918"
    u_values = {}
    for comp in ["roof", "outer wall", "window"]:
        u_values.update(
            {comp: [insul_standard_param.loc[yoc][comp],
                    insul_standard_param.loc["potential"][comp],
                    insul_standard_param.loc["periodical costs"][comp],
                    insul_standard_param.loc[
                        "periodical constraint costs"][comp]]})
        if comp == "roof":
            u_values[comp] \
             += [insul_standard_param.loc["potential flat"]["roof"],
                 insul_standard_param.loc["periodical costs flat"]["roof"],
                 insul_standard_param.loc["periodical constraint costs flat"]["roof"]]
    param_dict = {'comment': 'automatically_created',
                  'active': 1,
                  'sink': str(building_id) + "_heat_demand",
                  'temperature indoor': 20,
                  'heat limit temperature': 15}
    if areas[0]:
        window_dict = param_dict.copy()
        window_dict.update(
            {'label': str(building_id) + "_window",
             'U-value old': u_values["window"][0],
             'U-value new': u_values["window"][1],
             'area': areas[0],
             'periodical costs': u_values["window"][2],
             'periodical constraint costs': u_values["window"][3]})
        append_component("insulation", window_dict)

    if areas[1]:
        wall_dict = param_dict.copy()
        wall_dict.update(
            {'label': str(building_id) + "_wall",
             'U-value old': u_values["outer wall"][0],
             'U-value new': u_values["outer wall"][1],
             'area': areas[1],
             'periodical costs': u_values["outer wall"][2],
             'periodical constraint costs': u_values["outer wall"][3]})
        append_component("insulation", wall_dict)

    if areas[2]:
        u_value_new = u_values["roof"][4 if roof_type == "flat roof" else 1]
        periodical_costs = \
            u_values["roof"][5 if roof_type == "flat roof" else 2]
        roof_dict = param_dict.copy()
        roof_dict.update(
            {'label': str(building_id) + "_roof",
             'U-value old': u_values["roof"][0],
             'U-value new': u_value_new,
             'area': areas[2],
             'periodical costs': periodical_costs,
             'periodical constraint costs': u_values["roof"][3 if roof_type != "flat roof" else 6]})
        append_component("insulation", roof_dict)
