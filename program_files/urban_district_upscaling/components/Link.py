"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Janik Budde - janik.budde@fh-muenster.de
"""
import pandas


def create_link(label: str, bus_1: str, bus_2: str, link_type: str, sheets,
                standard_parameters: pandas.ExcelFile) -> dict:
    """
        Creates a link with standard_parameters, based on the standard
        parameters given in the "standard_parameters" dataset and adds
        it to the "sheets"-output dataset.
    
        :param label: label, the created link will be given
        :type label: str
        :param bus_1: label, of the first bus
        :type bus_1: str
        :param bus_2: label, of the second bus
        :type bus_2: str
        :param link_type: needed to get the standard parameters of the
                          link to be created
        :type link_type: str
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import create_standard_parameter_comp

    return create_standard_parameter_comp(
        specific_param={"label": label, "bus1": bus_1, "bus2": bus_2},
        standard_parameter_info=[link_type, "6_links", "link type"],
        sheets=sheets,
        standard_parameters=standard_parameters
    )


def create_central_electricity_bus_connection(
        cluster: str, sheets: dict, standard_parameters: pandas.ExcelFile
) -> dict:
    """
        In this method, clustered buildings are connected to the local
        electricity market. For this purpose, a link is created between
        the cluster power bus and the central power bus and, if
        available, another link between the cluster pv bus and the
        central power bus. These are attached to the return structure
        "sheets".
        
        :param cluster: Cluster id
        :type cluster: str
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    # add link from central electricity bus to cluster electricity bus
    if (cluster + "_central_electricity_link") not in sheets["links"].index:
        sheets = create_link(
            label=cluster + "_central_electricity_link",
            bus_1="central_electricity_bus",
            bus_2=cluster + "_electricity_bus",
            link_type="electricity central link decentral",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        sheets["links"].set_index("label", inplace=True, drop=False)
    # add link from cluster pv bus to cluster electricity bus
    if ((cluster + "_pv_" + cluster + "_electricity_link") not in list(sheets[
        "links"]["label"])
            and (cluster + "_pv_central") in sheets["links"].index):
        sheets = create_link(
            label=cluster + "_pv_" + cluster + "_electricity_link",
            bus_1=cluster + "_pv_bus",
            bus_2=cluster + "_electricity_bus",
            link_type="electricity photovoltaic decentral link decentral",
            sheets=sheets,
            standard_parameters=standard_parameters)
        sheets["links"].set_index("label", inplace=True, drop=False)
    return sheets


def create_cluster_pv_links(cluster: str, sheets: dict, sink_parameters: list,
                            standard_parameters: pandas.ExcelFile) -> dict:
    """
        In this method, the PV bus of the cluster is connected to the
        central electricity bus, if the cluster power demand > 0, it is
        also connected to the cluster power bus.
        
        :param cluster: Cluster ID
        :type cluster: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param sink_parameters: list holding the cluster's sinks \
            information e. g. the total res electricity demand [0]
        :type sink_parameters: list
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    if cluster + "_pv_central_electricity_link" not in sheets["links"].index:
        sheets = create_link(
            label=cluster + "_pv_central_electricity_link",
            bus_1=cluster + "_pv_bus",
            bus_2="central_electricity_bus",
            link_type="electricity photovoltaic decentral link central",
            sheets=sheets,
            standard_parameters=standard_parameters)
        
        # if the considered cluster has an electricity demand the link
        # between the cluster electricity bus and the cluster pv sources
        # will be created
        if sum(sink_parameters[0:3]):
            sheets = create_link(
                label=cluster + "_pv_electricity_link",
                bus_1=cluster + "_pv_bus",
                bus_2=cluster + "_electricity_bus",
                link_type="electricity photovoltaic decentral link decentral",
                sheets=sheets,
                standard_parameters=standard_parameters)
        sheets["links"].set_index("label", inplace=True, drop=False)
    return sheets


def add_cluster_naturalgas_bus_links(sheets: dict, cluster: str,
                                     standard_parameters: pandas.ExcelFile
                                     ) -> dict:
    """
        In this method, the naturalgas bus of the cluster is connected
        to the central natural gas bus.
        
        :param cluster: Cluster ID
        :type cluster: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    if (len(sheets["links"]) == 0 or cluster + "_central_natural_gas_link"
            not in list(sheets["links"]["label"])):
        sheets = create_link(
            label=cluster + "_central_natural_gas_link",
            bus_1="central_natural_gas_bus",
            bus_2=cluster + "_natural_gas_bus",
            link_type="natural gas central link decentral",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        sheets["links"].set_index("label", inplace=True, drop=False)
    return sheets


def delete_non_used_links(sheets_clustering: dict, building_labels: list,
                          sheets: dict) -> dict:
    """
        Within this method all non-clustered links which are no longer
        in use after the clustering process are removed and the
        
        :param sheets_clustering: copy of the model definition created \
            within the pre_processing.py
        :type sheets_clustering: dict
        :param building_labels: list containing the building labels of \
            the energy system to be clustered
        :type building_labels: list
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    
    # iterate threw all links that are within the sheets dictionary
    # this is necessary since sheets clustering is only a copy of the
    # un-clustered file while sheets will be changed within this method
    df_links = sheets_clustering["links"][sheets_clustering["links"][
        "label"].isin(sheets["links"].index)]
    for _, link in df_links.iterrows():
        # first label part
        label_part = link["label"].split("_")[0]
        # if the label doesn't begin with central_ and the
        # considered building's label is within the link label
        if label_part != "central" and label_part in building_labels:
            # remove the current link from sheets["links"]
            sheets["links"] = sheets["links"].drop(index=link["label"])
    return sheets
