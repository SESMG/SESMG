import olca_ipc as ipc
import olca_schema as o
import pandas as pd
import time

# aktuelle Annahme: alle möglichen Processe sind bereits in der Datenbank vorhanden (sonst create_process)
# TODO create product system: kann man aus mehreren processen ein product system erstellen oder geht das nicht???


# run the jason rpc protokoll
client = ipc.Client()


def get_the_corresponding_processes():
    """
    Get all the needed processes that are used to describe the energy system. Probably needs to be concected to
    the components.csv file.
    """

    # find multiple processes
    # TODO automatisiert auf die Technologien zugreifen über die components datei
    search_terms = ["8e9774f1-ef5c-4d45-82de-6ed01e2a2491", "4bf0b07d-cb0f-4b7f-b4f4-7ce99bd24f22"] #aktuell noch 2 System Processes

    # create an empty list for all needed processes
    all_processes = []

    # iterate through all components to select the processes
    for term in search_terms:
        processes = client.get(o.Process, term)  # get can be used to get multiple outputs in a list
        all_processes.append(processes)

    return all_processes


def create_product_system(all_processes):
    """
    Create the product systems.
        :param all_processes
        :type list
    """

    # set configutrations for not chosing automatic linking of the processes
    config = o.LinkingConfig(
        prefer_unit_processes=False,  # beim linking werden stattdessesn System Processes ausgewählt
        provider_linking=None,        # kein autolinking zulassen
    )

    # List to store the IDs of created product systems
    product_system_ids = []

    # iterate through all processes to create the needed product systems
    for process in all_processes:
        print(process.name)
        system_ref = client.create_product_system(process, config)
        product_system_ids.append(system_ref.id)
        print(f"created product system {system_ref.name}, id={system_ref.id}")

    print(product_system_ids)
    return product_system_ids


# TODO efficiencies anpassen / data harmonization
# TODO am Ende Produktsysteme die so schon erstellt wurden nicht nochmal erstellen, sondern auf die zurückgreifen
#  ansonsten ja beim jeden lauf neues Produktsystem (mit result.dispose!)


def calculate_results(product_system_ids):
    """
    Calculate the inventory of the system as well as the results of the impact assessment in one step
        :param product_system_ids
        :type list
    """

    # create empty dictionaries for the impacts and the inventory
    total_environmental_impacts = {}
    total_inventory_results = {}

    # Calculate the results for the electricity mix example
    for product_system in product_system_ids:

        setup = o.CalculationSetup(
            target=o.Ref(ref_type=o.RefType.ProductSystem, id=product_system),
            # unit automatically takes the unit of the quantitive reference
            impact_method=o.Ref(id="1f08b96a-0d3c-4e9e-88bf-09f2239f95e1"), # example: ReCiPe Midpoint H
            amount=1,  #hier später mit dem richtigen Amount verknüpfen,  #wahrscheinlich passen hierdurch die Werte nicht? Kann das sein?
            # ACHTUNG: kann allerdings ja dann nicht immer mit dem gleichen amount verknüpft werden!
            allocation=None,#keine allocation eingearbeit, lediglich von ProBas vordefiniert
                                # "amount of the reference flow of the calculation target for to which the result should be scaled"
            nw_set=None #kein normalization or weighting set
        )

        result = client.calculate(setup)
        result.wait_until_ready() #später hier noch n waiting print hinzufügen

        print(result)

        # get inventory
        # TODO auch wichtig später für die interpretation, dass der user auf die inventory results und die impact assessment
        #  results zugreifen kann!
        # TODO brauche ich das überhaupt? vielleicht bei der interpretation mit abfrage arbeiten um Laufzeit zu sparen?
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
        :param data
        :type
        :param category_col_name
        :type
        :param value_col_name
        :type
    """

    df = pd.DataFrame(
        [(category, value)
         for category, value in data.items()],
        columns=[category_col_name, value_col_name]
    )

    return df


# save the summarized results as a sub step in an excel file and dispose
# TODO Variablen hier richtig übergeben, das passt so noch nicht
def export_and_dispose(total_environmental_impacts_df, total_inventory_df):
"""
Export the given result to Excel and dispose it after the Export
        finished.
"""

    # TODO files her richtig angeben
    # TODO außerdem input / output anders darstellen
    environmental_impacts_file = 'total_environmental_impacts.xlsx'
    inventory_results_file = 'total_inventory_results.xlsx'

    # TODO nochmal gucken in dem github beispiel: client.excel_export
    total_environmental_impacts_df.to_excel(environmental_impacts_file, index=False)
    total_inventory_df.to_excel(inventory_results_file, index=False)

    # TODO dispose


# run program
# run preparational steps
all_processes = get_the_corresponding_processes()
product_system_ids = create_product_system(all_processes)
total_environmental_impacts, total_inventory_results = calculate_results(product_system_ids)

#create the two dfs
total_environmental_impacts_df = create_df_from_dict(total_environmental_impacts, "Impact category", "Total Value")
print(total_environmental_impacts_df)
total_inventory_df = create_df_from_dict(total_inventory_results, "Flow Name", "Amount")
print(total_inventory_df)

#save
export_and_dispose(total_environmental_impacts_df, total_inventory_df)