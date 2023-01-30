# TODO building intern heatpumps
# TODO battery storages
# TODO electric heating
# TODO Solarthermal
# TODO DH
# TODO differentiate between insulations
# TODO Central components?
# TODO clustered demands res com etc.
# TODO clustered solar thermal

import pandas

# dictionary that contains all attachments form us tool
label_dict = {
    "_electricity_demand":
        ["electricity demand", "input 1/kWh"],
    "_parcel_gchp_elec_link":
        ["electricity demand heat pump (GCHP)", "output 1/kWh"],
    "_electric_vehicle":
        ["electricity demand electric vehicle", "input 1/kWh"],
    "_electricity_bus_shortage":
        ["electricity purchase", "output 1/kWh"],
    "_hp_elec_bus_shortage":
        ["electricity purchase (heat pump)", "output 1/kWh"],
    "_central_electricity_link":
        ["electricity purchase (energy market)", "output 1/kWh"],
    "_pv_bus_excess":
        ["sale of electricity (PV)", "input 1/kWh"],
    "_pv_central_electricity_link":
        ["sale of electricity (market)", "input 1/kWh"],
    "_pv_self_consumption_electricity_link":
        ["self-consumption PV", "input 1/kWh"],
    "_heat_demand":
        ["heat demand", "input 1/kWh"],
    "_parcel_gchp_heat_link":
        ["heat supply heat pump", "input 1/kWh"],
    "_gas_bus_shortage":
        ["gas purchase", "output 1/kWh"],
    "_gasheating_transformer":
        ["heat supply (gas heating system)", "output 1/kWh"],
  }


def create_building_specific_results(us_sheet_raw_data: str,
                                     building_or_cluster: str,
                                     components_raw_data: str,
                                     result_path: str):
    """
    
        :param us_sheet_raw_data: Upscaling input sheet containing the \
            building data
        :type us_sheet_raw_data: str
        :param building_or_cluster: string defining rather a building \
            sharp or a clustered scenario is under investigation
        :type building_or_cluster: str
        :param components_raw_data: DataFrame holding the \
            components.csv file's content which is the result of one \
            optimization
        :type components_raw_data: str
        :param result_path: string containing the dictionary where the \
            resulting file is saved
    """
    us_sheet_raw_data = pandas.read_excel(us_sheet_raw_data)
    components_raw_data = pandas.read_csv(components_raw_data)
    # delete unit row
    us_sheet_data = us_sheet_raw_data[1:]
    # create list of labels
    if building_or_cluster == "building":
        list_of_buildings = us_sheet_data.label.values.tolist()
    else:
        list_of_buildings = us_sheet_data["cluster ID"].values.tolist()
        list_of_buildings = list(dict.fromkeys(list_of_buildings))
    
    # function 2
    # indices of columns with 0 capacity
    components_raw_data.drop(
        components_raw_data.loc[
            components_raw_data['capacity/kW'] == 0].index, inplace=True)
    
    overview = {}
    # for loop to match label_dict with list of buildings
    for building in list_of_buildings:
        overview[building] = {}
        for comp in label_dict:
            if str(building) + comp in components_raw_data["ID"].tolist():
                row = components_raw_data["ID"] == str(building) + comp
                components_raw_data_row = components_raw_data.loc[row]
                overview[building][label_dict.get(comp)[0]] = \
                    components_raw_data_row[label_dict.get(comp)[1]].values[0]
    
    overview_df_nan = pandas.DataFrame.from_dict(overview, orient="index")
    # replace nan values with 0
    overview_df = overview_df_nan.fillna(0)
    overview_df.to_csv(result_path + "/building_specific_results.csv")
