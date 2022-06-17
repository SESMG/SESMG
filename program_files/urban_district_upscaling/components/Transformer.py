def create_transformer(building_id, transformer_type,
                       building_type=None, area="None", specific="None",
                       output="None"):
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
    transf_dict = {
        "building_gchp_transformer": [
            '_gchp_transformer',
            '_hp_elec_bus',
            '_heat_bus',
            'None'],
        "building_ashp_transformer": [
            '_ashp_transformer',
            '_hp_elec_bus',
            '_heat_bus',
            'None'],
        'building_gasheating_transformer': [
            '_gasheating_transformer',
            '_gas_bus',
            '_heat_bus',
            'None'],
        "building_electricheating_transformer": [
            '_electricheating_transformer',
            '_electricity_bus',
            '_heat_bus',
            'None'],
        "central_" + specific + "_chp": [
            "_" + specific + '_chp_transformer',
            "_chp_" + specific + "_bus",
            "_chp_" + specific + "_elec_bus",
            output],
        "central_naturalgas_heating_plant_transformer": [
            "_" + specific + '_heating_plant_transformer',
            "_" + specific + "_plant_bus",
            output,
            "None"],
        "central_" + specific + "_transformer": [
            "_" + specific + "_transformer",
            "_heatpump_elec_bus",
            output,
            "None"],
        "central_biomass_transformer": [
            '_biomass_transformer',
            "_biomass_bus",
            output,
            "None"],
        "central_electrolysis_transformer": [
            "_electrolysis_transformer",
            "_electricity_bus",
            "_h2_bus",
            "None"],
        "central_methanization_transformer":[
            '_methanization_transformer',
             "_h2_bus",
            "_naturalgas_bus",
             "None"],
        "central_fuelcell_transformer": [
            '_fuelcell_transformer',
            "_h2_bus",
            "_electricity_bus",
            output]
    }
    
    if building_type is not None:
        if building_type == "RES":
            bus = 'building_res_gas_bus'
        elif building_type == "IND":
            bus = 'building_ind_gas_bus'
        else:
            bus = 'building_com_gas_bus'
            # building gas bus
        create_standard_parameter_bus(label=str(building_id) + "_gas_bus",
                                      bus_type=bus)
    create_standard_parameter_comp(
        specific_param={
            'label': str(building_id) + transf_dict.get(transformer_type)[0],
            'comment': 'automatically_created',
            'input': str(building_id) + transf_dict.get(transformer_type)[1],
            'output': (str(building_id) + transf_dict.get(transformer_type)[2])
            if output == "None" else output,
            'output2': transf_dict.get(transformer_type)[3],
            'area': area},
        type="transformers",
        index="comment",
        standard_param_name=transformer_type)
