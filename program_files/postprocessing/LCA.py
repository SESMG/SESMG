import olca_ipc as ipc
import olca_schema as o
import pandas as pd
import os

# TODO später beim erstellen mit der loc arbeiten, in der GUI eine Seite einfügen, in der eine optionale LCA gemacht wird?
# from create_results_prepare_data import df_list_of_components

# aktuelle Annahme: alle möglichen Processe sind bereits in der Datenbank vorhanden (sonst create_process)
# TODO create product system: kann man aus mehreren processen ein product system erstellen oder geht das nicht???

# run the jason rpc protokoll
client = ipc.Client()
# TODO Prüfen: Kann man den IPC Server auch automatisch starten?
#  ja kann man aber relativ kompliziert, also noch mal in Ruhe angucken oder Gregor fragen
#  https://github.com/GreenDelta/gdt-server
#  darüber kann man sogar auch die dispose results machen

# settings
pd.set_option('display.max_rows', None)  # Zeige alle Zeilen an
pd.set_option('display.max_columns', None)  # Zeige alle Spalten an
pd.set_option('display.width', None)  # Verwende die gesamte Breite des Terminals für die Anzeige


def user_input_model_run():
    """
    Ask the user for which model run he/she wants to have the lca result.
    INFO: Das ist jetzt erstmal eine Überbrückung zur Nutzung der components csv, damit dieser file läuft, später dann
    in den SESMG und die GUI implementieren
    """

    # user selects model run and therefore result
    input_model_run = "model_definition_basic_2024-01-11--15-38-46"  # input("Enter the model run you want to analyse")

    components_path = r"C:\Users\Franziska\Documents\SESMG\results\\" + input_model_run + "\\components.csv"

    # DataFrame aus der Excel-Datei erstellen
    df_list_of_components_copy = pd.read_csv(components_path)

    return df_list_of_components_copy


def add_lca_uuid(df_list_of_components_copy):
    """
    Create a dictionary containing the ID of the components the needed value and the uuid, based on a seperate CSV file.
        :param df_list_of_components_copy: DataFrame containing components.
        :type pd.DataFrame
    """

    # define path that contains the uuids
    uuid_path = r"C:\Users\Franziska\Documents\GitHub\SESMG\docs\lca\lca_uuids.csv"

    # import into a df
    df_list_of_uuid = pd.read_csv(uuid_path, usecols=[0, 1, 2])
    # TODO später die Info über den Type des Prozesses automatisiert beziehen

    # add the uuids to the right components
    merged_df_components_with_uuids = \
        pd.merge(df_list_of_components_copy, df_list_of_uuid, how='left', left_on='ID', right_on='ID')

    # create empty lca dict
    lca_dict = {}

    # iterate through the rows in the df
    for index, row in merged_df_components_with_uuids.iterrows():
        component_id = row['ID']
        output_value = row['output 1/kWh'] # TODO hier noch was anderes überlegen für die Technologien, die mehrere outputs haben
        component_type = row['Type']
        uuid = row['UUID']

        if not pd.isnull(uuid):
            lca_dict[component_id] = (output_value, component_type, uuid)

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




# run preparational steps
df_list_of_components_copy = user_input_model_run()
lca_dict = add_lca_uuid(df_list_of_components_copy)

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