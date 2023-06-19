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
    building_id: str, storage_type: str, de_centralized: str, sheets,
    standard_parameters, bus=None
):
    """
    Sets the specific parameters for a battery, and creates them
    afterwards.

    :param building_id: building label
    :type building_id: str
    :param storage_type:
    :type storage_type: str
    :param de_centralized:
    :type de_centralized: str
    :param bus:
    :type bus: str
    :param sheets:
    :type sheets:
    """
    from program_files.urban_district_upscaling.pre_processing import (
        create_standard_parameter_comp,
    )

    return create_standard_parameter_comp(
        specific_param={
            "label": str(building_id) + storage_dict.get(storage_type)[1],
            "comment": "automatically_created",
            "bus": str(building_id) + storage_dict.get(storage_type)[2]
            if bus is None
            else bus,
        },
        standard_parameter_info=[
            de_centralized + storage_dict.get(storage_type)[0],
            "5_storages",
            "comment",
        ],
        sheets=sheets,
        standard_parameters=standard_parameters
    )


def building_storages(building, true_bools, sheets, standard_parameters):
    """
    TODO
    :param building:
    :type building:
    :param true_bools:
    :type true_bools:
    :param sheets:
    :type sheets:
    """
    build_storage_dict = {"battery storage": "battery", "thermal storage": "thermal"}
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


def storage_clustering(building, sheets_clustering, storage_parameter, sheets):
    """
        Main method to collect the information about the storage
        (battery, thermal storage), which are located in the considered
        cluster.

        :param building: DataFrame containing the building row from the\
            pre scenario sheet
        :type building: pd.Dataframe
        :param sheets_clustering:
        :type sheets_clustering: pd.DataFrame
        :param storage_parameter: dictionary containing the collected \
            storage information
        :type storage_parameter: dict

        :return:
    """
    for index, storage in sheets_clustering["storages"].iterrows():
        label = storage["label"]
        # collect battery information
        if str(building[0]) in label and label in sheets["storages"].index:
            if label.split("_")[1] in ["battery", "thermal"]:
                storage_parameter, sheets = cluster_storage_information(
                    storage, storage_parameter, label.split("_")[1], sheets
                )
    # return the collected data to the main clustering method
    return storage_parameter, sheets


def cluster_storage_information(storage, storage_parameter, type, sheets):
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
        :param type: storage type needed to define the dict entry \
            to be modified
        :type type: str

        :return:
    """
    # counter
    storage_parameter[type][0] += 1
    # max invest
    storage_parameter[type][1] += storage["max. investment capacity"]
    # periodical costs
    storage_parameter[type][2] += storage["periodical costs"]
    # periodical constraint costs
    storage_parameter[type][3] += storage["periodical constraint costs"]
    if type == "thermal":
        # variable output costs
        storage_parameter[type][4] += storage["variable output costs"]
    # remove the considered storage from transformer sheet
    sheets["storages"] = sheets["storages"].drop(index=storage["label"])
    # return the modified transf_param dict to the transformer clustering
    # method
    return storage_parameter, sheets


def create_cluster_storage(type, cluster, storage_parameters, sheets):
    """

    :param standard_parameters:
    :param type:
    :return:
    """
    from program_files.urban_district_upscaling.pre_processing import (
        append_component,
        read_standard_parameters,
    )

    specific_dict = {
        "label": str(cluster) + storage_dict.get(type)[0],
        "comment": "automatically created",
        "bus": str(cluster) + storage_dict.get(type)[2],
    }
    standard_param, standard_keys = read_standard_parameters(
        "building" + storage_dict.get(type)[0], "storages", "comment"
    )
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        specific_dict[standard_keys[i]] = standard_param[standard_keys[i]]
    specific_dict.update(
        {
            "periodical costs": storage_parameters[type][2]
            / storage_parameters[type][0],
            "periodical constraint costs": storage_parameters[type][3]
            / storage_parameters[type][0],
            "max. investment capacity": storage_parameters[type][1],
        }
    )

    if type == "thermal":
        specific_dict["variable output costs"] = (
            storage_parameters[type][4] / storage_parameters[type][0]
        )
    # produce a pandas series out of the dict above due to easier
    # appending
    return append_component(sheets, "storages", specific_dict)
