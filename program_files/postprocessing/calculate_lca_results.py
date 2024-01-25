import olca_ipc as ipc
import olca_schema as o
import pandas as pd
import os
import re


# aktuelle Annahme: alle möglichen Processe sind bereits in der Datenbank vorhanden (sonst create_process)
# TODO create product system: kann man aus mehreren processen ein product system erstellen oder geht das nicht???

# run the jason rpc protokoll
client = ipc.Client()
# TODO Prüfen: Kann man den IPC Server auch automatisch starten?
#  ja kann man aber relativ kompliziert, also noch mal in Ruhe angucken oder Gregor fragen
#  https://github.com/GreenDelta/gdt-server
#  darüber kann man sogar auch die dispose results machen

# settings
#pd.set_option('display.max_rows', None)  # Zeige alle Zeilen an
#pd.set_option('display.max_columns', None)  # Zeige alle Spalten an
#pd.set_option('display.width', None)  # Verwende die gesamte Breite des Terminals für die Anzeige


def selected_model_run(path: str):
    """
    Später hier mal testen, wie man es lösen kann wenn schon Ergebnisse für den Lauf vorliegen, also den auf den
    result_path direkt zugreifen.
    Wahrscheinlich auch wichtig für die Ergebnisse von Pareto-Läufen!
    """


def add_uuid_to_components(nodes_data, components_list):
    """
    This function adds the right uuids to the components_list for the further result processing.
        :param nodes_data: contains all informationen from the model definition sorted in a dict with the different
            sheet names as keys
        :type nodes_data: dict
        :param components_list: part of the results, contains all components of the final energy system as well
            as there technical and economical values
        :type components_list: pd.DataFrame

    :return: - **components_list** (list) - copy of the list containing the additional uuids.
    """

    # create dict for uuids
    uuid_mapping = {}

    # loop through the different sheets of the nodes_data dict
    for key, values in nodes_data.items():

        # eliminate sheets that are not needed for the lca caluclation
        if key.lower() not in ["timeseries", "weather data", "pipe types",
                               "competition constraints", "energysystem", "district heating", "insulation"]:

            # loop through each row of the dataframe in the values of the dict
            for index, row in values.iterrows():
                row_first_value = row.iloc[0]  # First value in current row
                row_last_value = row.iloc[-1]  # Last value in current row

                # If there's a match, add the uuid to the matching components
                # if not matching_components.empty:
                uuid_mapping[row_first_value] = row_last_value

                print("mapping")
                print(uuid_mapping)

    # TODO heat sink window hat hier noch einen fehler!
    # remove 'shortage' and 'excess' in components_list['ID']
    components_list['ID'] = components_list['ID'].apply(lambda x: re.sub(r'_shortage$', '', x))
    components_list['ID'] = components_list['ID'].apply(lambda x: re.sub(r'_excess$', '', x))

    # adds the uuids to the components list
    components_list['uuid'] = components_list['ID'].map(uuid_mapping)

    print(components_list)
    return components_list


def add_lca_uuid(components):
    """
    Create a dictionary containing the ID of the components the needed value and the uuid, based on a seperate CSV file.
        :param components: DataFrame containing components.
        :type pd.DataFrame
    """

    # TODO brauche ich zusätzlich eine Info über den Typ des Prozesses
    # TODO das brauche ich eigentlich nur wenn ich safe ProBas nehme
    # get type of the process out of the name

    # create empty lca dict
    lca_dict = {}

    # iterate through the rows in the df
    for index, row in components.iterrows():
        component_id = row['ID']
        output_value = row['output 1/kWh'] # TODO hier noch was anderes überlegen für die Technologien, die mehrere outputs haben
        component_type = "system" #row['Type']
        uuid = row['uuid']

        if not pd.isnull(uuid):
            lca_dict[component_id] = (output_value, uuid, component_type, )

    print("first lca dict")
    print(lca_dict)
    return lca_dict
    # TODO überlegen ob die Infos Grundsätzlich über ein dict oder einen df übergeben werden sollten

def create_product_system(lca_dict):
    """
    Create the product systems.
        :param lca_dict: containing the information about the energy system: names, output values, process type and
            the uuid.
        :type dict
    """

    # set configutrations for not chosing automatic linking of the processes
    config = o.LinkingConfig(
        prefer_unit_processes=False,  # beim linking werden stattdessesn System Processes ausgewählt
        provider_linking=None,        # kein autolinking zulassen
    )

    # List to store created system_refs
    system_refs = []

    # iterate through each component of the dictionary
    for component_id, (output_value, component_type, uuid) in lca_dict.items():
        # check if the component is a system
        if component_type == 'system':
            # create product system
            system_ref = client.create_product_system(client.get(o.Process, uuid), config)
            # update lca_dict with uuid2
            lca_dict[component_id] = (output_value, component_type, uuid, system_ref.id)
            # add the created system_ref to the list
            system_refs.append(system_ref)

    print("lca dict_new")
    print(lca_dict)

    return lca_dict, system_refs


# TODO efficiencies anpassen / data harmonization
# TODO am Ende Produktsysteme die so schon erstellt wurden nicht nochmal erstellen, sondern auf die zurückgreifen
#  ansonsten ja beim jeden lauf neues Produktsystem (mit result.dispose!)


def modify_unit_processes():
    """
    wahrscheinlich lösen mit Process Link = connection between two processes in a product system
    Allerdings nochmal hinten angestellt, das muss ich nur machen wenn ich 100%ig ProBas verwende!
    """
    None


def calculate_results(lca_dict):
    """
    Calculate the inventory of the system as well as the results of the impact assessment in one step
        :param lca_dict
        :type dict
    """

    # create empty dictionaries for the impacts and the inventory
    total_environmental_impacts = {}
    total_inventory_results = {}

    # Calculate the results for the electricity mix example
    # for product_system in product_system_ids:
    for component_id, (output_value, component_type, uuid, uuid2) in lca_dict.items():
    # TODO doch eventuell mit einer productsystem ids liste arbeiten, da das für die laufzeit wahrscheinlich
    #  effizienter ist ?
    # TODO nochmal prüfen, ob das jetzt so auch mit mehreren werten noch klappt

        setup = o.CalculationSetup(
            target=o.Ref(ref_type=o.RefType.ProductSystem, id=uuid2),
            # unit automatically takes the unit of the quantitive reference
            impact_method=o.Ref(id="1f08b96a-0d3c-4e9e-88bf-09f2239f95e1"), # example: ReCiPe Midpoint H
            amount=output_value,
            allocation=None,        # no allocation, already predefined by ProBas
            nw_set=None             # no normalization or weighting set
        )

        result = client.calculate(setup)
        result.wait_until_ready() #später hier noch n waiting print hinzufügen

        print(result)

        # get inventory
        # TODO grundsätzlich wichtig für interpretation, vielleicht später abfrage arbeiten um Laufzeit zu sparen?
        # TODO außerdem auch wichtgit, wenn ich mich dazu entscheide die flows selber ein bischen zu analysieren,
        #  und nicht nur das vorhefertigte impact assessment verwende
        inventory = result.get_total_flows()

        # TODO noch testen wie berücksichtigt wird ob es input oder output ist, also nochmal händisch überprüfen

        for i in inventory:
            flow_name = i.envi_flow.flow.name
            if flow_name not in total_inventory_results:
                total_inventory_results[flow_name] = {"amount": 0, "direction": i.envi_flow.is_input}
            total_inventory_results[flow_name] =+ i.amount

        # get results for the impact categories
        impact_categories = result.get_total_impacts()

        # summarize the results for the different product systems over the impact categories
        for i in impact_categories:
            impact_category_name = i.impact_category.name
            if impact_category_name not in total_environmental_impacts:
                total_environmental_impacts[impact_category_name] = 0
            total_environmental_impacts[impact_category_name] += i.amount

        return total_environmental_impacts, total_inventory_results


def create_df_from_dict(data, category_col_name, value_col_name):
    """
    Turn the two dictionaries for the inventory and the impact assessment results into dataframes for
        :param data: dicitonary with data
        :type dict
        :param category_col_name: name of the category column
        :type str
        :param value_col_name: name of the value column
        :type str
    """

    df = pd.DataFrame(
        [(category, value)
         for category, value in data.items()],
        columns=[category_col_name, value_col_name]
    )

    return df


# save the summarized results as a sub step in an excel file and dispose
def export_and_save(total_environmental_impacts_df, total_inventory_df, system_refs):
    """
    Export the given result to Excel and dispose it after the Export
        finished.
        :param total_inventory_df
        :type pd.DataFrame
        :param total_environmental_impacts_df
        :type pd.Dataframe
    """
    # TODO input / output in den Ergebnissen noch anders darstellen

    result_path = r"C:\Users\Franziska\Documents\SESMG\results"

    # define the path for the excel files
    excel_file1 = os.path.join(result_path, 'Inventory Results.xlsx')
    excel_file2 = os.path.join(result_path, 'Total Environmental Impacts.xlsx')

    # save dfs as excel files
    total_inventory_df.to_excel(excel_file1, index=False)
    total_environmental_impacts_df.to_excel(excel_file2, index=False)

    print("Results were succesfully saved as excel files")

    print("SR")
    print(system_refs)


    # TODO Dispose nochmal prüfen, geht eigentlich nur bei results und delete nur bei datasets
    #  alternativ beim productsystem erstellen prüfen ob es das genannte schon gibt
    # Speichern der IDs der Produktionsysteme
    #system_ids = [system_ref.id for system_ref in system_refs]

    # dispose the no longer needed product systems
    #for system_id in system_ids:
    #   client.delete(o.Ref(id=system_id))

    #print("Product systems were disposed")



def calculate_lca_results_function (path: str, components: pd.DataFrame):

    # run preparational steps
    lca_dict = add_lca_uuid(components)

    print("lca dict")
    print(lca_dict)

    # run openlca steps
    lca_dict, system_refs = create_product_system(lca_dict)
    total_environmental_impacts, total_inventory_results = calculate_results(lca_dict)

    #create the two dfs
    total_environmental_impacts_df = create_df_from_dict(total_environmental_impacts, "Impact category", "Total Value")
    total_inventory_df = create_df_from_dict(total_inventory_results, "Flow Name", "Amount")
    print(total_environmental_impacts_df)
    print(total_inventory_df)

    # save the summarized results as a sub step in an excel file and dispose
    export_and_save(total_environmental_impacts_df, total_inventory_df, system_refs)