def create_gchp(parcel_id, area, standard_parameters):
    """
        Sets the specific parameters for a ground coupled heat pump
        system, and creates them afterwards.

        :param parcel_id: parcel label
        :type parcel_id: str
        :param area: parcel area which can be used for gchp anergy
        :type area: float
        :param standard_parameters: Dataframe holding gchp specific
                                    standard parameters
        :type standard_parameters: pd.Dataframe
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_comp
    # TODO
    #probe_length = \
    #    transformers_standard_parameters.loc['building_gchp_transformer'][
    #        'length of the geoth. probe']
    #heat_extraction = \
    #    transformers_standard_parameters.loc['building_gchp_transformer'][
    #        'heat extraction']
    #min_bore_hole_area = \
    #    transformers_standard_parameters.loc['building_gchp_transformer'][
    #        'min. borehole area']
    
    create_standard_parameter_comp(
        specific_param={'label': str(parcel_id) + '_gchp_transformer',
                        'comment': 'automatically_created',
                        'input': str(parcel_id) + '_hp_elec_bus',
                        'output': str(parcel_id) + '_heat_bus',
                        'output2': 'None',
                        'area': area,
                        'existing capacity': 0,
                        'min. investment capacity': 0},
        standard_parameters=standard_parameters,
        type="transformers",
        index="comment",
        standard_param_name="building_gchp_transformer")


def create_ashp(building_id, standard_parameters):
    """
        Sets the specific parameters for an air source heatpump system,
        and creates them afterwards.

        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding ashp specific
                                    standard parameters
        :type standard_parameters: pd.Dataframe
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_comp
    create_standard_parameter_comp(
        specific_param={'label': (str(building_id) + '_ashp_transformer'),
                        'comment': 'automatically_created',
                        'input': str(building_id) + '_hp_elec_bus',
                        'output': str(building_id) + '_heat_bus',
                        'output2': 'None',
                        'existing capacity': 0,
                        'min. investment capacity': 0},
        standard_parameters=standard_parameters,
        type="transformers",
        index="comment",
        standard_param_name="building_ashp_transformer")


def create_gas_heating(building_id, building_type, standard_parameters):
    """
        Sets the specific parameters for a gas heating system,
        and creates them afterwards.

        :param building_id: building label
        :type building_id: str
        :param building_type: defines rather the usage is residential
                              or commercial
        :type building_type: str
        :param standard_parameters: Dataframe holding ashp specific
                                    standard parameters
        :type standard_parameters: pd.Dataframe
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_bus, create_standard_parameter_comp
    
    if building_type == "RES":
        bus = 'building_res_gas_bus'
    elif building_type == "IND":
        bus = 'building_ind_gas_bus'
    else:
        bus = 'building_com_gas_bus'
    # building gas bus
    create_standard_parameter_bus(label=str(building_id) + "_gas_bus",
                                  bus_type=bus,
                                  standard_parameters=standard_parameters)

    create_standard_parameter_comp(
        specific_param={'label': str(building_id) + '_gasheating_transformer',
                        'comment': 'automatically_created',
                        'input': str(building_id) + '_gas_bus',
                        'output': str(building_id) + '_heat_bus',
                        'output2': 'None'},
        standard_parameters=standard_parameters,
        type="transformers",
        index="comment",
        standard_param_name='building_gasheating_transformer')


def create_electric_heating(building_id, standard_parameters):
    """
        Sets the specific parameters for an electric heating system,
        and creates them afterwards.

        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding electric heating
                                    specific standard parameters
        :type standard_parameters: pd.Dataframe
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_comp
    create_standard_parameter_comp(
        specific_param={
            'label': str(building_id) + '_electricheating_transformer',
            'comment': 'automatically_created',
            'input': str(building_id) + '_electricity_bus',
            'output': str(building_id) + '_heat_bus',
            'output2': 'None'},
        standard_parameters=standard_parameters,
        type="tranformers",
        index="comment",
        standard_param_name="building_electricheating_transformer")
