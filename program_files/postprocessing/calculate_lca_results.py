import logging

import olca_ipc as ipc
import olca_schema as o
import pandas as pd
import os
import re

# aktuelle Annahme: alle möglichen Processe sind bereits in der Datenbank vorhanden (sonst create_process)
# TODO Speicher Prozess dazu selbst erstellen!

# run the jason rpc protokoll
client = ipc.Client()
# TODO Prüfen: Kann man den IPC Server auch automatisch starten?
#  ja kann man aber relativ kompliziert, also noch mal in Ruhe angucken oder Gregor fragen
#  https://github.com/GreenDelta/gdt-server
#  darüber kann man sogar auch die dispose results machen


# TODO kann man später eventuell automatisiert über die pints bib machen
def change_unit(value_old_unit):
    """
    Change the unit from kWh to TJ which is the unit for energy in openLCA
        :param value_old_unit
        :type value_old_unit: str
    :return: - **value_new_unit** (str) -
    """
    value_new_unit = 3.6 * 10**(-6) * value_old_unit
    return value_new_unit


def add_uuid_to_components(nodes_data, components_list):
    """
    This function adds the right uuids to the components_list for the further result processing.
        :param nodes_data: contains all informationen from the model definition sorted in a dict with the different
            sheet names as keys
        :type nodes_data: dict
        :param components_list: part of the results, contains all components of the final energy system as well
            as there technical and economical values
        :type components_list: pd.DataFrame

    :return: - **components_list** (pd.DataFrame) - copy of the df containing the additional uuids.
    """

    #print("node")
    #print(nodes_data.items())

    # create dict for uuids
    uuid_mapping = {}

    # loop through the different sheets of the nodes_data dict
    for key, values in nodes_data.items():

        # eliminate sheets that are not needed for the lca caluclation
        if key.lower() not in ["timeseries", "weather data", "pipe types",
                               "competition constraints", "energysystem", "district heating"]: #, "insulation"]:

            # loop through each row of the dataframe in the values of the dict
            for index, row in values.iterrows():
                row_first_value = row.iloc[0]  # First value in current row
                row_last_value = row.iloc[-1]  # Last value in current row

                # If there's a match, add the uuid to the matching components
                uuid_mapping[row_first_value] = row_last_value

    # TODO heat sink window insulation erkennt zusätzlich Spalten nicht an, vielleicht einmal Gregor fragen
    #  kein Fehler, nur komisch
    # remove 'shortage' and 'excess' in components_list['ID']
    components_list['ID'] = components_list['ID'].apply(lambda x: re.sub(r'_shortage$', '', x))
    components_list['ID'] = components_list['ID'].apply(lambda x: re.sub(r'_excess$', '', x))

    # adds the uuids to the components list
    components_list['uuid'] = components_list['ID'].map(uuid_mapping)

    print(components_list)
    print(type(components_list))
    return components_list


def consider_var_cost_factor(components_list, variable_cost_factor):
    """
    Adjusts specific columns in the given DataFrame by multiplying them with the provided variable cost factor.

        :param components_list: DataFrame containing the components data.
        :type components_list: pandas.core.frame.DataFrame
        :param variable_cost_factor: Factor to scale specific columns in the DataFrame.
        :type variable_cost_factor: float
    """

    # Indexer for columns 3 to 6 (0-based)
    columns_to_multiply = components_list.columns[2:6]

    # Multiplication by the variable_cost_factor
    components_list[columns_to_multiply] *= variable_cost_factor


def add_lca_uuid(components):
    """
    Create a dictionary containing the ID of the components the needed value and the uuid, based on a seperate CSV file.
        :param components: DataFrame containing components.
        :type pd.DataFrame
    """

    # create empty lca dict
    lca_dict = {}

    # iterate through the rows in the df
    for index, row in components.iterrows():
        uuid = row['uuid']

        if uuid is not None and uuid != '' and not pd.isna(uuid):  # TODO Check if uuid is not None or an empty string
            # TODO wenn insulation Frage geklärt, kann diese Zeile vereinfacht werden

            component_id = row['ID']
            output_value_old = row['output 1/kWh'] # TODO hier noch was anderes überlegen für die Technologien, die mehrere outputs haben

            # change unit to TJ (unit in the database)
            output_value = change_unit(output_value_old) #TODO vielleicht noch vereinheitlicht an anderer Stelle besser

            uuid = row['uuid']
            # get the right process based on the uuid
            process_ref = client.get(o.Process, uuid)
            # extract the type of the process
            component_type = "System" if "System" in process_ref.name else "Unit" if "Unit" in process_ref.name else "Unknown"
            # TODO brauche ich bei anderer Datenbank nicht
            # fill lca dict with all important information
            lca_dict[component_id] = (output_value, uuid, component_type, )

    return lca_dict


def change_values_of_input_processes(lca_dict):
    """
        :param lca_dict
        :type lca_dict: dict
    """

    #print(lca_dict)

    # TODO Achtung aktuell von dem Unit Prozess
    #  am Ende überlegen ob so beibehalten oder schon in OpenLCA anpassen, um mehr unsicherheiten zu vermeiden?
    # Provider Ref
    # TODO muss noch automatisiert werden
    gas_uuid = "1f57d050-a740-445a-ab26-955df9ed9095"

    # iterate through each component of the dictionary
    for component_id, (output_value, uuid, component_type) in lca_dict.items():

        # TODO so anpassen, dass es auch für anere Technologien funktioniert, so nur provisorisch für Gas
        if component_id == 'ID_gas_bus':
            gas_input = output_value
            gas_uuid == uuid

        # check if the component is a system
        if component_type == 'Unit':

            # get the right input flow
            process_ref = client.get(o.Process, uuid)

            # loop through the different exchanges (the inputs and outputs of a process)
            for exchange in process_ref.exchanges:

                # check if there are inputs and outputs with a default provider
                if exchange.default_provider is not None:
                    default_provider_ref = exchange.default_provider
                    ref_id = default_provider_ref.id

                    # check of some of the providers are already at another place in the energy system
                    # goal here is to harmonize the data
                    # TODO hier die uuid aus dem anderen process nehmen
                    if gas_uuid == ref_id:
                        exchange.amount = gas_input/output_value
                        # TODO entweder input value hinzufügen oder output value von dem Gasstrom? was ist besser?
                        #  aktuell wird einfach output value von dem Gasstrom hinzugefügt
                        print("new values were added to the process flows")
                        # change value(s) in the database
                        client.put(process_ref)


def create_product_system(lca_dict):
    """
    Create the product systems.
        :param lca_dict: containing the information about the energy system: names, output values, process type and
            the uuid.
        :type dict
    """

    # set configurations for not choosing automatic linking of the processes
    config1 = o.LinkingConfig(
        prefer_unit_processes=False,  # do not choose automatic linking, but chose own system processes
        provider_linking=None,
    )

    # set configuration for the unit processes that are manually connected
    config2 = o.LinkingConfig(
        prefer_unit_processes=False,
        provider_linking=o.ProviderLinking.IGNORE_DEFAULTS
    )

    # List to store created system_refs
    system_refs = []

    # iterate through each component of the dictionary
    for component_id, (output_value, uuid, component_type) in lca_dict.items():

        # check if the component is a system
        if component_type == 'System':
            # create product system
            system_ref = client.create_product_system(client.get(o.Process, uuid), config1)
            # update lca_dict with uuid2
            lca_dict[component_id] = (output_value, component_type, uuid, system_ref.id)
            # add the created system_ref to the list
            system_refs.append(system_ref)

        # check if the component is a system
        if component_type == 'Unit':

            # TODO noch ne schönere Lösung überlegen, auch für andere Beispiele
            if component_id == 'ID_gas_bus':
                continue

            else:
                # create product system
                system_ref = client.create_product_system(client.get(o.Process, uuid), config2)

                print("product system created")
                print(system_ref)

                # update lca_dict with uuid2
                lca_dict[component_id] = (output_value, component_type, uuid, system_ref.id)
                # add the created system_ref to the list
                system_refs.append(system_ref)

    print("lca dict_new")
    print(lca_dict)

    return lca_dict, system_refs


def calculate_results(lca_dict):
    """
    Calculate the inventory of the system as well as the results of the impact assessment in one step
        :param lca_dict
        :type dict

    :return: - **total_environmental_impacts** (dict)
    :return: - **total_inventory_results** (dict)
    """

    # create empty dictionaries for the impacts and the inventory
    total_environmental_impacts = {}
    total_inventory_results = {}

    # calculate the product systems only for the components where product systems were created earlier
    for component_id, values in lca_dict.items():
        if len(values) == 4:
            output_value, component_type, uuid, uuid2 = values

            # Größenordnungen überprüfen
            print("output")
            print(output_value)

            # calculation setup
            setup = o.CalculationSetup(
                target=o.Ref(ref_type=o.RefType.ProductSystem, id=uuid2),
                # unit automatically takes the unit of the quantitive reference
                impact_method=o.Ref(id="1f08b96a-0d3c-4e9e-88bf-09f2239f95e1"),  # example: ReCiPe Midpoint H # TODO auch noch anpassen
                amount=output_value,    # assumption: linear correlation with the output value
                allocation=None,        # no allocation, already predefined by ProBas
                nw_set=None             # no normalization or weighting set
            )

            result = client.calculate(setup)
            result.wait_until_ready()             # TODO später hier noch n waiting print hinzufügen

            # get inventory
            inventory = result.get_total_flows()

            # loop through each flow in the inventory
            for i in inventory:
                flow_name = i.envi_flow.flow.name
                # check if the flow is already in the inventory, if not add it
                if flow_name not in total_inventory_results:
                    total_inventory_results[flow_name] = \
                        {"amount": 0, "unit": i.envi_flow.flow.ref_unit, "direction": i.envi_flow.is_input}
                total_inventory_results[flow_name]["amount"] += i.amount

            # get results for the impact categories
            impact_categories = result.get_total_impacts()

            # summarize the results for the different product systems over the impact categories
            for i in impact_categories:
                impact_category_name = i.impact_category.name
                if impact_category_name not in total_environmental_impacts:
                    total_environmental_impacts[impact_category_name] = \
                        {"amount": 0, "unit": i.impact_category.ref_unit}
                total_environmental_impacts[impact_category_name]["amount"] += i.amount

            # dispose results
            result.dispose

    return total_environmental_impacts, total_inventory_results


def create_dataframes(total_inventory_results, total_environmental_impacts):
    """
    Creates Pandas DataFrames from total environmental impacts and inventory results
        :param total_inventory_results: dictionary containing inventory results, where the key is the
                                    flow name and the value is a dictionary with 'amount', 'unit', and 'direction'
        :type total_inventory_results: dict
        :param total_environmental_impacts: dictionary containing environmental impacts, where the key is the
                                         flow name and the value is a dictionary with 'amount' and 'unit'
        :type total_environmental_impacts: dict

    :return: - **inventory_df** (pandas.DataFrame)
    :return: - **impacts_df** (pandas.DataFrame)
    """

    # create df from the inventory dictionary
    inventory_df = pd.DataFrame([(key, data['amount'], data['unit'], data['direction']) for
                                 key, data in total_inventory_results.items()],
                                columns=['flow_name', 'value', 'unit', 'input_flow'])

    # create df from the impact assessment dictionary
    impacts_df = pd.DataFrame([(key, data['amount'], data['unit']) for
                                 key, data in total_environmental_impacts.items()],
                                columns=['flow_name', 'value', 'unit'])

    print("result dfs")
    print(inventory_df)
    print(impacts_df)

    return inventory_df, impacts_df


# save the summarized results as a sub step in an excel file and dispose
def export_and_save(inventory_df, impacts_df, path):
    """
    Export the given result to Excel and dispose it after the Export
        finished.
        :param inventory_df
        :type inventory_df: pd.DataFrame
        :param impacts_df
        :type impacts_df: pd.Dataframe
        :param path
        :type path: str
    """
    # TODO Eventuell input / output in den Ergebnissen noch anders darstellen

    # define the path for the .xlsx files
    excel_file1 = os.path.join(path, 'inventory_results.xlsx')
    excel_file2 = os.path.join(path, 'total_environmental_impacts.xlsx')

    # save dfs as excel files
    inventory_df.to_excel(excel_file1, index=False)
    impacts_df.to_excel(excel_file2, index=False)

    print("Results were successfully saved as excel files")


def delete_product_systems(system_refs):
    """
    Delete not longer needed product systems from the database
        :param system_refs
        :type system_refs: list
    """
    # TODO alternativ später beim productsystem erstellen prüfen ob es das genannte schon gibt
    # save the IDs of the product systems
    system_ids = [system_ref.id for system_ref in system_refs]

    # dispose the no longer needed product systems
    #for system_id in system_ids:
     #   client.delete(o.Ref(ref_type=o.RefType.ProductSystem,id=system_id))
      #  print("Product systems were disposed")


def calculate_lca_results_function(path: str, components: pd.DataFrame):
    """
    Combine different functions to calculate the different lca results for a simulation as well as for the
    different pareto points, if selected.
        :param path
        :type path: str
        :param components
        :type components: pd.DataFrame
    """

    # create the lca dict to prepare for the further lca calculation
    lca_dict = add_lca_uuid(components)

    # data harmonization
    change_values_of_input_processes(lca_dict)

    # run openlca steps
    lca_dict, system_refs = create_product_system(lca_dict)
    total_environmental_impacts, total_inventory_results = calculate_results(lca_dict)

    # create the two dfs
    inventory_df, impacts_df = create_dataframes(total_inventory_results, total_environmental_impacts, )

    # save the summarized results as a sub step in an excel file and dispose
    export_and_save(inventory_df, impacts_df, path)

    # delete no longer needed product systems
    delete_product_systems(system_refs)