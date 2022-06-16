def create_battery(building_id: str, standard_parameters, storage_type: str):
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
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_comp
    create_standard_parameter_comp(
        specific_param={
            'label': str(building_id) + '_battery_storage',
            'comment': 'automatically_created',
            'bus': str(building_id) + '_electricity_bus'},
        standard_parameters=standard_parameters,
        type="storages",
        index="comment",
        standard_param_name=storage_type + '_battery_storage')


def create_thermal_storage(building_id, standard_parameters,
                           storage_type: str, bus=None):
    """
        TODO DOCSTRING TEXT
        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding thermal storage
                                    specific standard parameters
        :type standard_parameters: pd.Dataframe
        :param storage_type:
        :type storage_type: str
        :param bus:
        :type bus: str
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_comp
    create_standard_parameter_comp(
        specific_param={
            'label': str(building_id) + '_thermal_storage',
            'comment': 'automatically_created',
            'bus': str(building_id) + '_heat_bus' if bus is None else bus},
        standard_parameters=standard_parameters,
        type="storages",
        index="comment",
        standard_param_name=storage_type + '_thermal_storage')