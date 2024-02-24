import olca_ipc as ipc
import olca_schema as o
import pandas as pd
import os
import re


# run the jason rpc protokoll
client = ipc.Client()
# todo start ipc server automatically:  https://github.com/GreenDelta/gdt-server


def change_unit(value_old_unit):
    """
    Change the unit from kWh to MJ which is the unit for the reference flow of energy in openLCA
        :param value_old_unit
        :type value_old_unit: str
    :return: - **value_new_unit** (str) -
    """
    value_new_unit = 3.6 * value_old_unit

    return value_new_unit


def add_uuid_to_components(nodes_data, components_list):
    """
    Add UUIDs to the components_list based on the information in nodes_data.
        :param nodes_data: contains all information from the model definition sorted in a dict with the different
            sheet names as keys
        :type nodes_data: dict
        :param components_list: part of the results, contains all components of the final energy system as well
            as there technical and economical values
        :type components_list: pd.DataFrame

    :return: - **components_list** (pd.DataFrame) - copy of the df containing the additional uuids.
    """
    # create dict for uuids
    uuid_mapping = {}

    # loop through the different sheets of the nodes_data dict
    for key, values in nodes_data.items():

        # eliminate sheets that are not needed for the lca caluclation
        if key.lower() not in ["timeseries", "weather data", "pipe types",
                               "competition constraints", "energysystem", "district heating"]:

            # loop through each row of the dataframe in the values of the dict
            for index, row in values.iterrows():
                row_first_value = row.iloc[0]  # First value in current row
                row_uuid_value = row['lca uuid']  # uuid value in current row

                # add "insulation" to the ID of the heat_sink_window
                row_first_value += "-insulation" if key == "insulation" else ""

                # check whether the component has in "input" or "output" column for later adaptions
                input_value = row.get("input", "None")
                output_value = row.get("output", "None")

                # If there's a match, add the uuid and input value to the matching components
                uuid_mapping[row_first_value] = {'uuid': row_uuid_value, 'input': input_value, 'output': output_value}

    # remove 'shortage' in components_list['ID']
    components_list['ID'] = components_list['ID'].apply(lambda x: re.sub(r'_shortage$', '', x))

    # adds the uuids and input values to the components list
    components_list[['uuid', 'input', 'output']] = components_list['ID'].map(
        lambda x: uuid_mapping.get(x, {'uuid': None, 'input': None, 'output': None})).apply(pd.Series)

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


def change_components_list_for_excess(components):
    """
    Subtract the outputs from the excess buses to consider the consumption base approach for the environmental impacts.
        :param components: Dataframe containing components data
        :type components: pandas.core.frame.DataFrame

    :return: - **components2** (DataFrame) - copy of the components DataFrame with changes in the sources that provide
                excess energy
    """

    # handle excess buses by subtracting the impacts
    for index, row in components.iterrows():

        # check if the row has an output that needs to be subtracted for the energy excess
        if row['output'] is not None and row['output'] != "None":

            # add '_excess' to the string
            excess_bus = row['output'] + '_excess'

            if excess_bus in components['ID'].values:

                # subtract the excess value from the output value of the source
                components.loc[components['output'] == row['output'], 'output 1/kWh'] -= \
                    components.loc[components['ID'] == excess_bus, 'input 1/kWh'].values[0]

    # create copy
    components2 = components.copy()

    return components2


def change_components_list_to_avoid_double_counting(components2):
    """
    Filter the DataFrame 'components' to extract components with an uuid and avoid double counting of environmental
    impacts by subtracting some components from the output values.
        :param components2: DataFrame containing components data.
        :type components2: pandas.core.frame.DataFrame

    :return: - **filtered_components** (DataFrame)
    """

    # filter through the rows of the df and select only rows with an added uuid and non-zero output values
    filtered_components = components2[(components2['uuid'] != '') & (components2['output 1/kWh'] != 0)]

    # iterate through the rows in the df
    for index, row in filtered_components.iterrows():

        # define the name of the columns
        change_input_flow = row['input']

        # assure to use the electricity input, as the columns are chosen randomly
        input_value_old = min(row['input 1/kWh'], row['input 2/kWh']) if row['input 2/kWh'] != 0 else row['input 1/kWh']

        # remove the input values of the components that are considered twice in the results
        # remove the gas heating transformer example from this operation
        # todo könnte man auch automatisiert machen, nachdem die unit prozesse zusammengeführt wurden
        # todo etwas aufwendiger und daher erstmal rausgelassen
        if change_input_flow in filtered_components['ID'].values and change_input_flow != "01_gas_bus":
            filtered_components.loc[
                filtered_components['ID'] == change_input_flow, 'output 1/kWh'] -= input_value_old

    print("FILTERED")
    print(filtered_components.to_string())

    return filtered_components


def add_lca_uuid(filtered_components):
    """
    Create a dictionary containing the ID of the components the needed value and the uuid, based on the .csv file.
        :param filtered_components: DataFrame containing components.
        :type filtered_components:pd.DataFrame

    :return: - **lca_dict** (dict) - dictionary containing information about components, their input flows,
                output values, uuid and components type
    """

    # create empty lca dict
    lca_dict = {}

    # iterate through the rows in the df
    for index, row in filtered_components.iterrows():
        uuid = row['uuid']
        component_id = row['ID']
        output_value_old = row['output 1/kWh']
        change_input_flow = row['input']

        # change unit to TJ (unit in the database)
        output_value = change_unit(output_value_old)

        # get the right process based on the uuid
        process_ref = client.get(o.Process, uuid)
        # extract the type of the process (note: this is database specific)
        component_type = "System" if "LCI" in process_ref.name else "Unit" \
            if "UP" in process_ref.name else "Unknown"

        # combine entries with the same LCA uuid
        if uuid in [value[2] for value in lca_dict.values()]:
            # Search for the row with the matching uuid now
            for existing_row_id, existing_row_values in lca_dict.items():
                # combine putput values
                new_output_value = lca_dict[existing_row_id][1] + output_value
                # create new tuple
                updated_values = (
                    lca_dict[existing_row_id][0],
                    new_output_value,
                    lca_dict[existing_row_id][2],
                    lca_dict[existing_row_id][3],)
                # update the value
                lca_dict[existing_row_id] = updated_values

        else:
            # fill lca dict with all important information
            lca_dict[component_id] = (change_input_flow, output_value, uuid, component_type, )

    return lca_dict


def change_values_of_input_processes(lca_dict):
    """
    Change values of input processes in the lca_dict based on harmonization with other processes
        :param lca_dict: Dictionary containing needed information for the lca about the components of the energy system.
        :type lca_dict: dict

    :return: - **lca_dict** (dict) - dictionary without the components that are now already considered in another
                product system
    """

    # create copy of the dictionary
    lca_dict_copy = dict(lca_dict)

    # iterate through each component of the dictionary
    for component_id, (change_input_flow, output_value, uuid, component_type) in lca_dict_copy.items():

        # check weather the component is a unit process and has an input that needs to be harmonized
        if change_input_flow != "None" and component_type == 'Unit':

            # get the corresponding uuid and output of the component that in listed as an input flow from the lca_dict
            selected_uuid = lca_dict.get(change_input_flow, [None, None, None, None])[2]
            selected_output = lca_dict.get(change_input_flow, [None, None, None, None])[1]

            # get the right input flow
            process_ref = client.get(o.Process, uuid)

            # loop through the different exchanges (the inputs and outputs of a process)
            for exchange in process_ref.exchanges:

                # check if there are inputs and outputs with a default provider
                if exchange.default_provider is not None:
                    default_provider_ref = exchange.default_provider
                    ref_id = default_provider_ref.id

                    # check of some of the default provider can be harmonized
                    if selected_uuid == ref_id:
                        exchange.amount = selected_output / output_value
                        # because of the relation of the outputs no influence on the unit of the new value
                        print("new values were added to the process flows for the")
                        print(component_id)
                        print(exchange.amount)
                        # change value(s) in the database
                        client.put(process_ref)

            # remove the input flows thar are already considered from the dict to avoid double counting
            del lca_dict[change_input_flow]

    return lca_dict


def create_product_system(lca_dict):
    """
    Create the product systems.

        :param lca_dict: Containing the information about the energy system: names, output values, process type, and the uuid.
        :type: dict

    :return: - **lca_dict** (dict): Updated dictionary with system_refs added.
    :return: - **system_refs** (list): List to store created system_refs.
    """

    # set configurations for not choosing automatic linking of the processes
    config1 = o.LinkingConfig(
        prefer_unit_processes=False,  # do not choose automatic linking, but chose own system processes
        provider_linking=None)

    # set configuration for the unit processes that are manually connected
    config2 = o.LinkingConfig(
        prefer_unit_processes=False,
        provider_linking=o.ProviderLinking.ONLY_DEFAULTS)   # "onlydefaults"

    # List to store created system_refs
    system_refs = []

    # Iterate through each component of the dictionary
    for component_id, (change_input_flow, output_value, uuid, component_type) in lca_dict.items():
        # Create product system based on conditions
        if component_type == 'System' or (component_type == 'Unit' and change_input_flow != "None"):
            config = config1 if component_type == 'System' else config2
            # Create product system
            system_ref = client.create_product_system(client.get(o.Process, uuid), config)
            # Update lca_dict with uuid2
            lca_dict[component_id] = (change_input_flow, output_value, component_type, uuid, system_ref.id)
            # Add the created system_ref to the list
            system_refs.append(system_ref)

    print("lca dict_new")
    print(lca_dict)

    return lca_dict, system_refs


def calculate_results(lca_dict):
    """
    Calculate the inventory and impact assessment results for the energy system based on the provided lca_dict.
        :param lca_dict: Dictionary containing information about the energy system
        :type: dict

    :return: - **total_environmental_impacts** (dict)
    :return: - **total_inventory_results** (dict)
    """

    # create empty dictionaries for the impacts and the inventory
    environmental_impacts = {}
    total_inventory_results = {}

    # calculate the product systems only for the components where product systems were created earlier
    for component_id, values in lca_dict.items():
        if len(values) == 5:
            change_input_flow, output_value, component_type, uuid, uuid2 = values

            # calculation setup
            setup = o.CalculationSetup(
                target=o.Ref(ref_type=o.RefType.ProductSystem, id=uuid2),
                # unit automatically takes the unit of the quantitive reference
                impact_method=o.Ref(id="1f08b96a-0d3c-4e9e-88bf-09f2239f95e1"),
                # ReCiPe Midpoint H # TODO add the impact assessment method as an option in the gui
                amount=output_value,    # assumption: linear correlation with the output value
                allocation=None,        # no allocation, already predefined by ProBas
                nw_set=None             # no normalization or weighting set
            )

            result = client.calculate(setup)
            result.wait_until_ready()

            # Get inventory and impact categories
            inventory = result.get_total_flows()
            impact_categories = result.get_total_impacts()

            # Loop through each flow in the inventory
            for i in inventory:
                flow_name = f"{i.envi_flow.flow.name} {i.envi_flow.flow.category}"
                total_inventory_results.setdefault(flow_name, {"amount": 0, "unit": i.envi_flow.flow.ref_unit,
                                                               "direction": i.envi_flow.is_input})
                total_inventory_results[flow_name]["amount"] += i.amount

            # Impact categories separated by technologies
            for i in impact_categories:
                impact_category_name = i.impact_category.name

                # Create a tuple for the specific impact category and the sum
                impact_tuple = (impact_category_name, component_id)
                sum_tuple = (impact_category_name, "sum")

                # Ensure the tuples exist in the dictionary with default values
                environmental_impacts.setdefault(impact_tuple, {"amount": 0, "unit": i.impact_category.ref_unit})
                environmental_impacts.setdefault(sum_tuple, {"amount": 0, "unit": i.impact_category.ref_unit})

                # Update the amounts for the specific impact category and the sum
                environmental_impacts[impact_tuple]["amount"] += i.amount
                environmental_impacts[sum_tuple]["amount"] += i.amount

            # dispose results
            result.dispose

    return environmental_impacts, total_inventory_results


def sort_environmental_impacts_dict(environmental_impacts):
    """
    Sort the environmental impact dictionary.
    :param environmental_impacts: Dictionary containing environmental impacts.
    :type environmental_impacts: dict

    :return: - **total_environmental_impacts** (dict): sorted dictionary containing environmental impacts
    """

    # Sort dict (all components per impact category listed)
    sorted_impacts = sorted(environmental_impacts.items(), key=lambda x: (x[0][0], x[0][1] != "sum", x[0][1]))

    # create a new dictionary with the sorted values
    total_environmental_impacts = {}
    for key, value in sorted_impacts:
        total_environmental_impacts[key] = value

    return total_environmental_impacts


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
    :return: - **impacts_df_summarized** (pandas.DataFrame)
    :return: - **impacts_df_components** (pandas.DataFrame)
    """

    # create df from the inventory dictionary
    inventory_df = pd.DataFrame([(key, data['amount'], data['unit'], data['direction']) for
                                 key, data in total_inventory_results.items()],
                                columns=['flow_name', 'value', 'unit', 'input_flow'])

    # create df from the impact assessment dictionary with 'sum' as the second value in the tuple
    impacts_df_summarized = pd.DataFrame([(key[0], data['amount'], data['unit']) for
                                          key, data in total_environmental_impacts.items() if key[1] == 'sum'],
                                         columns=['impact_category_name', 'value', 'unit'])

    impacts_df_components = pd.DataFrame([(*key, data['amount'], data['unit']) for
                               key, data in total_environmental_impacts.items()],
                              columns=['impact_category_name', 'component_id', 'value', 'unit'])

    print("result dfs")
    print(inventory_df)
    print(impacts_df_summarized)
    print(impacts_df_components)

    return inventory_df, impacts_df_summarized, impacts_df_components


def export_and_save(inventory_df, impacts_df_summarized, impacts_df_components, path):
    """
    Export the given result to Excel and dispose it after the Export
        finished.
        :param inventory_df
        :type inventory_df: pd.DataFrame
        :param impacts_df_summarized
        :type impacts_df_summarized: pd.Dataframe
        :param impacts_df_components
        :type impacts_df_components: pd.Dataframe
        :param path
        :type path: str
    """

    # Define the path for the .xlsx file
    excel_file = os.path.join(path, 'lca_results.xlsx')

    # Create ExcelWriter object
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        # Save inventory_df in the first sheet
        inventory_df.to_excel(writer, sheet_name='inventory_results', index=False)

        # Save impacts_df_summarized in the second sheet
        impacts_df_summarized.to_excel(writer, sheet_name='summarized', index=False)

        # Save impacts_df_components in the third sheet
        impacts_df_components.to_excel(writer, sheet_name='components', index=False)

    print("Results were successfully saved as excel files")


def delete_product_systems(system_refs):
    """
    Delete no longer needed product systems from the database.
        :param system_refs
        :type system_refs: list
    """
    # TODO store created product systems to reduce calculation for already created systems
    # save the IDs of the product systems
    system_ids = [system_ref.id for system_ref in system_refs]

    # dispose the no longer needed product systems
    for system_id in system_ids:
        client.delete(o.Ref(ref_type=o.RefType.ProductSystem,id=system_id))
        print("Product systems were disposed")


def calculate_lca_results_function(path: str, components: pd.DataFrame):
    """
    Combine different functions to calculate the different lca results for a simulation as well as for the
    different pareto points, if selected.
        :param path: path to result folder
        :type path: str
        :param components: lis
        :type components: pd.DataFrame
    """

    # consider the excess bus with negative impacts
    components2 = change_components_list_for_excess(components)

    # changes to the components DataFrame
    filtered_components = change_components_list_to_avoid_double_counting(components2)

    # create the lca dict to prepare for the further lca calculation
    lca_dict = add_lca_uuid(filtered_components)

    # data harmonization
    change_values_of_input_processes(lca_dict)

    # run openlca steps
    lca_dict, system_refs = create_product_system(lca_dict)
    environmental_impacts, total_inventory_results = calculate_results(lca_dict)

    # sort environmental impacts dict
    total_environmental_impacts = sort_environmental_impacts_dict(environmental_impacts)

    # create the two dfs
    inventory_df, impacts_df_summarized, impacts_df_components = \
        create_dataframes(total_inventory_results, total_environmental_impacts)

    # save the summarized results as a sub step in an .xlsx file and dispose
    export_and_save(inventory_df, impacts_df_summarized, impacts_df_components, path)

    # delete no longer needed product systems
    delete_product_systems(system_refs)


def collect_impact_categories(dataframes: dict, result_path: str):
    """
        Function to collect results sorted for each impact category. These results are later used to create the
        diagrams for the impact amounts.

        :param dataframes: dictionary containing the results for the different pareto runs, with the reduction values
            of the run as a key and a DataFrame as a value containing all the results for the run
        :type dataframes: dict
        :param result_path: path to later write the collected impact amounts in a new result file.
        :type result_path: str

    """
    # create empty dict for impact amounts
    impact_amounts_dict = {}

    # iterate threw the pareto points and hte lca_results components
    for key, values in dataframes.items():

        # go through each row in the values
        for index, row in values.iterrows():
            for category_name in [row["impact_category_name"]]:

                # combine key and the impact category
                key_with_category = (key, category_name)

                # loop through each key and create an entry in the impact_amounts_dict
                if key_with_category not in impact_amounts_dict:
                    impact_amounts_dict[key_with_category] = [("reductionco2", 100 * float(key))]
                impact_amounts_dict[key_with_category].append((row["component_id"], row["value"]))

    # create empty dict
    category_dfs = {}

    # loop through each entry in the impact_amounts_dicts
    for (key, category_name), values in impact_amounts_dict.items():
        # turn values in a DataFrame with the columns "component_ID" und "value"
        temp_df = pd.DataFrame(values, columns=['component_ID', 'value']).transpose()

        # use first row as columns name and remove first row from the df
        temp_df.columns = temp_df.iloc[0]
        temp_df = temp_df[1:]

        if category_name not in category_dfs:
            category_dfs[category_name] = temp_df

        else:
            category_dfs[category_name] = \
                pd.concat([category_dfs[category_name], temp_df], ignore_index=True, sort=False)

    # add columns as first row for the creation of the diagram
    for category_name, df in category_dfs.items():
        columns_as_row = pd.DataFrame([df.columns.tolist()], columns=df.columns)
        updated_df = pd.concat([columns_as_row, df], ignore_index=True)
        # update the df in the category_df dict
        category_dfs[category_name] = updated_df

    # create an ExcelWriter object
    with pd.ExcelWriter(result_path + "/impact_amounts.xlsx", engine='xlsxwriter') as writer:
        # save each category in a separate sheet
        for category, results in category_dfs.items():
            if category not in ("Ozone depletion", "Ionising radiation", "Agricultural land occupation",
                                "Urban land occupation", "Natural land transformation"):
                results.to_excel(writer, sheet_name=category, index=False, header=False)