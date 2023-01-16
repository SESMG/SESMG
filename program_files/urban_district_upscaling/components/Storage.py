import pandas

storage_dict = {
    "battery": ["_battery_storage", "_battery_storage", "_electricity_bus"],
    "thermal": ["_thermal_storage", "_thermal_storage", "_heat_bus"],
    "h2_storage": ["_h2_storage", "_h2_storage", "_h2_bus"],
    "naturalgas_storage": [
        "_naturalgas_storage",
        "_naturalgas_storage",
        "_naturalgas_bus",
    ],
}


def create_storage(
    building_id: str, storage_type: str, de_centralized: str, sheets: dict,
    standard_parameters: pandas.ExcelFile, bus=None
):
    """
        Sets the specific parameters for a battery, and creates them
        afterwards.
    
        :param building_id: building label
        :type building_id: str
        :param storage_type: string which definies which storage type \
            will be created
        :type storage_type: str
        :param de_centralized: string which differentiates rather the \
            created storage will be placed in a building (building) or \
            central (central)
        :type de_centralized: str
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param bus: string which contains a bus label which is \
            necessary if the storage should not be connected to the \
            standardized bus
        :type bus: str
    """
    from program_files import create_standard_parameter_comp

    return create_standard_parameter_comp(
        specific_param={
            "label": str(building_id) + storage_dict.get(storage_type)[1],
            "bus": str(building_id) + storage_dict.get(storage_type)[2]
            if bus is None
            else bus,
        },
        standard_parameter_info=[
            de_centralized + storage_dict.get(storage_type)[0],
            "5_storages",
            "storage_type",
        ],
        sheets=sheets,
        standard_parameters=standard_parameters
    )


def building_storages(building: dict, true_bools: list, sheets: dict,
                      standard_parameters: pandas.ExcelFile) -> dict:
    """
        TODO
        :param building: dictionary containing the building specific \
            parameters
        :type building: dict
        :param true_bools: list containing the entries that are \
            evaluated as true
        :type true_bools: list
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
    """
    build_storage_dict = {
        "battery storage": "battery", "thermal storage": "thermal"
    }
    
    for storage in build_storage_dict:
        if building[storage] in true_bools:
            sheets = create_storage(
                building_id=building["label"],
                sheets=sheets,
                storage_type=build_storage_dict[storage],
                de_centralized="building",
                standard_parameters=standard_parameters
            )
    
    return sheets


def storage_clustering(building: list, sheets_clustering: dict,
                       storage_parameter: dict, sheets: dict):
    """
        Main method to collect the information about the storage
        (battery, thermal storage), which are located in the considered
        cluster.

        :param building: list containing the building label [0], the \
            building's parcel ID [1] and the building type [2]
        :type building: list
        :param sheets_clustering: copy of the scenario created within \
            the pre_processing.py
        :type sheets_clustering: dict
        :param storage_parameter: dictionary containing the collected \
            storage information
        :type storage_parameter: dict
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
    """
    for index, storage in sheets_clustering["storages"].iterrows():
        label = storage["label"]
        # collect battery information
        if str(building[0]) in label and label in sheets["storages"].index:
            if label.split("_")[1] in ["battery", "thermal"]:
                storage_parameter, sheets = cluster_storage_information(
                    storage=storage,
                    storage_parameter=storage_parameter,
                    storage_type=label.split("_")[1],
                    sheets=sheets
                )
    # return the collected data to the main clustering method
    return storage_parameter, sheets


def cluster_storage_information(storage: pandas.Series,
                                storage_parameter: dict, storage_type: str,
                                sheets: dict):
    """
        Collects the transformer information of the selected type, and
        inserts it into the dict containing the cluster specific
        transformer data.

        :param storage: Dataframe containing the storage under \
            investigation
        :type storage: pd.DataFrame
        :param storage_parameter: dictionary containing the cluster \
            summed storage information
        :type storage_parameter: dict
        :param storage_type: storage type needed to define the dict entry \
            to be modified
        :type storage_type: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
    """
    # counter
    storage_parameter[storage_type][0] += 1
    # max invest
    storage_parameter[storage_type][1] += storage["max. investment capacity"]
    # periodical costs
    storage_parameter[storage_type][2] += storage["periodical costs"]
    # periodical constraint costs
    storage_parameter[storage_type][3] \
        += storage["periodical constraint costs"]
    # variable output costs
    storage_parameter[storage_type][4] += storage["variable output costs"]
    # remove the considered storage from transformer sheet
    sheets["storages"] = sheets["storages"].drop(index=storage["label"])
    # return the modified storage_parameter dict to the storage
    # clustering method
    return storage_parameter, sheets


def create_cluster_storage(storage_type: str, cluster: str,
                           storage_parameter: dict, sheets: dict,
                           standard_parameters: pandas.ExcelFile):
    """
        This method is used to create the clustered storages.
        
        :param storage_type: str which defines the storage type to be \
             created within this method
        :type storage_type: str
        :param storage_parameter: dictionary containing the cluster summed \
                source information
        :type storage_parameter: dict
        :param cluster: Cluster id
        :type cluster: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
    """
    from program_files.urban_district_upscaling.pre_processing import (
        append_component,
        read_standard_parameters,
    )
    specific_dict = {}
    # load the storage standard parameter
    standard_param, standard_keys = read_standard_parameters(
            name="building" + storage_dict.get(storage_type)[0],
            param_type="5_storages",
            index="storage_type",
            standard_parameters=standard_parameters)
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        specific_dict[standard_keys[i]] = standard_param[standard_keys[i]]
        
    counter = storage_parameter[storage_type][0]
    # define the storage specific parameter
    specific_dict.update({
        "label": str(cluster) + storage_dict.get(storage_type)[0],
        "bus": str(cluster) + storage_dict.get(storage_type)[2],
        "periodical costs": storage_parameter[storage_type][2] / counter,
        "periodical constraint costs": storage_parameter[storage_type][3]
                                       / counter,
        "max. investment capacity": storage_parameter[storage_type][1],
        "variable output costs": storage_parameter[storage_type][4] / counter
    })
    
    # produce a pandas series out of the dict above due to easier
    # appending
    return append_component(sheets, "storages", specific_dict)
