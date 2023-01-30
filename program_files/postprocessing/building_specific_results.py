import pandas as pd
import os

building_or_cluster = "building"
# function 1
# import us sheet for labels
us_sheet_raw_data = pd.read_excel("us_sheet_dev.xlsx")
# delete unit row
us_sheet_data = us_sheet_raw_data[1:]
# create list of labels
if building_or_cluster == "building":
    list_of_buildings = us_sheet_data.label.values.tolist()
else:
    list_of_buildings = us_sheet_data["cluster ID"].values.tolist()
    list_of_buildings = list(dict.fromkeys(list_of_buildings))

# function 2
components_raw_data = pd.read_csv("components.csv")
components_raw_data.drop(components_raw_data.loc[components_raw_data['capacity/kW'] == 0].index, inplace=True)
list_of_id = components_raw_data[components_raw_data.columns[0]].values.tolist()

# dictionary that contains all attachments form us tool
label_dict = {"_electricity_demand": ["electricity demand", "input 1/kWh"],
              "_parcel_gchp_elec_link": ["electricity demand heat pump", "output 1/kWh"],
              "_electric_vehicle": ["electricity demand electric vehicle", "input 1/kWh"],
              "_electricity_bus_shortage": ["electricity purchase", "output 1/kWh"],
              "_hp_elec_bus_shortage": ["electricity purchase (heat pump)", "output 1/kWh"],
              "_central_electricity_link": ["electricity purchase (energy market)", "output 1/kWh"],
              "_pv_bus_excess": ["sale of electricity (PV)", "input 1/kWh"],
              "_pv_central_electricity_link": ["sale of electricity (market)", "input 1/kWh"],
              "_pv_self_electricity_link": ["self-consumption PV", "input 1/kWh"],
              "_heat_demand": ["heat demand", "input 1/kWh"],
              "_parcel_gchp_heat_link": ["heat supply heat pump", "input 1/kWh"],
              "_gas_bus_shortage": ["gas purchase", "output 1/kWh"],
              "_gasheating_transformer": ["heat supply (gas heating system)", "output 1/kWh"],
              }
overview = {}
# for loop to match label_dict with list of buildings
for building in list_of_buildings:
    overview[building] = {}
    for comp in label_dict:
        if str(building) + comp in components_raw_data["ID"].tolist():
            components_raw_data_row = components_raw_data.loc[components_raw_data["ID"] == str(building) + comp]
            overview[building][label_dict.get(comp)[0]] = components_raw_data_row[label_dict.get(comp)[1]].values[0]

overview_df_nan = pd.DataFrame.from_dict(overview, orient="index")
# replace nan values with 0
overview_df = overview_df_nan.fillna(0)
print(overview_df)
