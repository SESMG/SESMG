def create_standard_parameter_sink(sink_type: str, label: str,
                                   sink_input: str, annual_demand: int,
                                   standard_parameters):
    """
        creates a sink with standard_parameters, based on the standard
        parameters given in the "standard_parameters" dataset and adds
        it to the "sheets"-output dataset.

        :param sink_type: needed to get the standard parameters of the
                          link to be created
        :type sink_type: str
        :param label: label, the created sink will be given
        :type label: str
        :param sink_input: label of the bus which will be the input of the
                      sink to be created
        :type sink_input: str
        :param annual_demand: #todo formula
        :type annual_demand: int
        :param standard_parameters: pandas Dataframe holding the
               information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_comp
    create_standard_parameter_comp(
        specific_param={'label': label,
                        'input': sink_input,
                        'annual demand': annual_demand},
        type="sinks",
        index="sink_type",
        standard_param_name=sink_type)
    

def create_sinks(sink_id: str, building_type: str, units: int,
                 occupants: int, yoc: str, area: int, standard_parameters):
    """
        TODO DOCSTRING
    """
    # electricity demand
    if building_type not in ['None', '0', 0]:
        # residential parameters
        demand_el = 0
        # get sinks standard parameters
        sinks_standard_param = standard_parameters.parse('sinks')
        sinks_standard_param.set_index("sink_type", inplace=True)
        
        if "RES" in building_type:
            elec_demand_res = {}
            standard_param = standard_parameters.parse('ResElecDemand')
            for i in range(len(standard_param)):
                elec_demand_res[standard_param['household size'][i]] = \
                    [standard_param[building_type + ' (kWh/a)'][i]]

            if occupants <= 5:
                demand_el = elec_demand_res[occupants][0] * units
            elif occupants > 5:
                demand_el = (elec_demand_res[5][0]) / 5 * occupants * units
        else:
            # commercial parameters
            elec_demand_com_ind = standard_parameters.parse(
                    'ComElecDemand' if "COM" in building_type
                    else "IndElecDemand")

            elec_demand_com_ind.set_index("commercial type", inplace=True)
            demand_el = elec_demand_com_ind.loc[building_type][
                'specific demand (kWh/(sqm a))']
            net_floor_area = area * sinks_standard_param.loc[
                building_type + "_electricity_sink"]['net_floor_area / area']
            demand_el *= net_floor_area

        create_standard_parameter_sink(
            sink_type=building_type + "_electricity_sink",
            label=str(sink_id) + "_electricity_demand",
            sink_input=str(sink_id) + "_electricity_bus",
            annual_demand=demand_el,
            standard_parameters=standard_parameters)

        # heat demand
        if "RES" in building_type:
            # read standard values from standard_parameter-dataset
            heat_demand_standard_param = \
                standard_parameters.parse('ResHeatDemand')
        elif "COM" in building_type:
            heat_demand_standard_param = \
                standard_parameters.parse('ComHeatDemand')
        elif "IND" in building_type:
            heat_demand_standard_param = \
                standard_parameters.parse('IndHeatDemand')
        else:
            raise ValueError("building_type does not exist")
        heat_demand_standard_param.set_index(
            "year of construction", inplace=True)
        if int(yoc) <= 1918:  # TODO
            yoc = "<1918"
        if units > 12:
            units = "> 12"
        if "RES" in building_type:
            specific_heat_demand = \
                heat_demand_standard_param.loc[yoc][str(units) + ' unit(s)']
        else:
            specific_heat_demand = \
                heat_demand_standard_param.loc[yoc][building_type]
        net_floor_area = area * sinks_standard_param \
            .loc[building_type + "_heat_sink"]['net_floor_area / area']
        demand_heat = specific_heat_demand * net_floor_area

        create_standard_parameter_sink(sink_type=building_type + "_heat_sink",
                                       label=str(sink_id) + "_heat_demand",
                                       sink_input=str(sink_id) + "_heat_bus",
                                       annual_demand=demand_heat,
                                       standard_parameters=standard_parameters)


def sink_clustering(building, sink, sink_parameters):
    """
        In this method, the current sinks of the respective cluster are
        stored in dict and the current sinks are deleted. Furthermore,
        the heat buses and heat requirements of each cluster are
        collected in order to summarize them afterwards.

        :param building: DataFrame containing the building row from the\
            pre scenario sheet
        :type building: pd.Dataframe
        :param sink: sink dataframe
        :type sink: pd.Dataframe
        :parameter sink_parameters: list containing clusters' sinks \
            information
        :type sink_parameters: list
    """
    # get cluster electricity sinks
    if str(building[0]) in sink["label"] \
            and "electricity" in sink["label"]:
        # get res elec demand
        if "RES" in building[2]:
            sink_parameters[0] += sink["annual demand"]
            sink_parameters[7].append(sink["label"])
            # sheets["sinks"] = sheets["sinks"].drop(index=sink["label"])
        # get com elec demand
        elif "COM" in building[2]:
            sink_parameters[1] += sink["annual demand"]
            sink_parameters[8].append(sink["label"])
            # sheets["sinks"] = sheets["sinks"].drop(index=sink["label"])
        # get ind elec demand
        elif "IND" in building[2]:
            sink_parameters[2] += sink["annual demand"]
            sink_parameters[9].append(sink["label"])
            # sheets["sinks"] = sheets["sinks"].drop(index=sink["label"])
    # get cluster heat sinks
    elif str(building[0]) in sink["label"] \
            and "heat" in sink["label"]:
        # append heat bus to cluster heat buses
        sink_parameters[3].append((building[2], sink["input"]))
        # get res heat demand
        if "RES" in building[2]:
            sink_parameters[4] += sink["annual demand"]
        # get com heat demand
        elif "COM" in building[2]:
            sink_parameters[5] += sink["annual demand"]
        # get ind heat demand
        elif "IND" in building[2]:
            sink_parameters[6] += sink["annual demand"]
        sink_parameters[7].append((building[2], sink["label"]))
    return sink_parameters

