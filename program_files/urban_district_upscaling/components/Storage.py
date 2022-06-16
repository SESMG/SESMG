def create_storage(building_id: str, standard_parameters, storage_type: str,
                   de_centralized: str, bus=None):
    """
        Sets the specific parameters for a battery, and creates them
        afterwards.

        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding battery
                                    specific standard parameters
        :type standard_parameters: pd.Dataframe
        :param storage_type:
        :type storage_type: str
        :param de_centralized:
        :type de_centralized: str
        :param bus:
        :type bus: str
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_comp
    storage_dict = {
        "battery": [de_centralized + '_battery_storage',
                    str(building_id) + '_battery_storage',
                    str(building_id) + '_electricity_bus'],
        "thermal": [de_centralized + '_thermal_storage',
                    str(building_id) + '_thermal_storage',
                    str(building_id) + '_heat_bus' if bus is None else bus],
        "h2_storage": [de_centralized + "_h2_storage",
                       str(building_id) + "_h2_storage",
                       str(building_id) + "_h2_bus"],
        "natural_gas_storage": [de_centralized + "_naturalgas_storage",
                                str(building_id) + "_naturalgas_storage",
                                str(building_id) + "_naturalgas_bus"]}
    
    create_standard_parameter_comp(
        specific_param={'label': storage_dict.get(storage_type)[1],
                        'comment': 'automatically_created',
                        'bus': storage_dict.get(storage_type)[2]},
        standard_parameters=standard_parameters,
        type="storages",
        index="comment",
        standard_param_name=storage_dict.get(storage_type)[0])
