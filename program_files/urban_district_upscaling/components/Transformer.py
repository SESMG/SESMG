def create_transformer(building_id, standard_parameters, transformer_type,
                       building_type=None, area="None"):
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_bus, create_standard_parameter_comp

    # TODO for gchps
    # probe_length = \
    #    transformers_standard_parameters.loc['building_gchp_transformer'][
    #        'length of the geoth. probe']
    # heat_extraction = \
    #    transformers_standard_parameters.loc['building_gchp_transformer'][
    #        'heat extraction']
    # min_bore_hole_area = \
    #    transformers_standard_parameters.loc['building_gchp_transformer'][
    #        'min. borehole area']
    transformer_dict = {
        "building_gchp_transformer": [str(building_id) + '_gchp_transformer',
                                      str(building_id) + '_hp_elec_bus',
                                      str(building_id) + '_heat_bus',
                                      'None',
                                      area],
        "building_ashp_transformer": [str(building_id) + '_ashp_transformer',
                                      str(building_id) + '_hp_elec_bus',
                                      str(building_id) + '_heat_bus',
                                      'None',
                                      'None'],
        'building_gasheating_transformer': [
            str(building_id) + '_gasheating_transformer',
            str(building_id) + '_gas_bus',
            str(building_id) + '_heat_bus',
            'None',
            'None'],
        "building_electricheating_transformer": [
            str(building_id) + '_electricheating_transformer',
            str(building_id) + '_electricity_bus',
            str(building_id) + '_heat_bus',
            'None',
            'None']}
    if building_type is not None:
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
        specific_param={
            'label': transformer_dict.get(transformer_type)[0],
            'comment': 'automatically_created',
            'input': transformer_dict.get(transformer_type)[1],
            'output': transformer_dict.get(transformer_type)[2],
            'output2': transformer_dict.get(transformer_type)[3],
            'area': transformer_dict.get(transformer_type)[4]},
        standard_parameters=standard_parameters,
        type="transformers",
        index="comment",
        standard_param_name=transformer_type)
