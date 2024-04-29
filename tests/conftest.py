import pytest
import pandas
import os


@pytest.fixture
def test_storage_decentralized_battery_entry():
    """
        Manually create a standard parameter building battery storage
        to validate functionality of several methods.
    """
    storages = import_standard_parameter_data(label="5_storages")
    storage = storages.query("`storage type` == 'battery storage decentral'")
    # combine specific data and the standard parameter data
    sheets = {"storages": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_building_battery_storage"],
                "storage type": ["battery storage decentral"],
                "bus": ["test_building_electricity_bus"],
                "min. investment capacity": [float(0)]}),
            right=storage,
            left_on="storage type",
            right_on="storage type"
            )}

    # remove column which was used to merge the two dataframe parts
    sheets["storages"] = sheets["storages"].drop(columns=["storage type"])

    return sheets


def compare_flow_attributes(flows, flows_test):
    """
    
    """
    if len(list(flows.keys())) > 0:
        flow_test_method = flows[list(flows.keys())[0]]
        flow_compare = flows_test[list(flows_test.keys())[0]]
        if hasattr(flow_test_method, "emission_factor"):
            assert flow_test_method.emission_factor \
                   == flow_compare.emission_factor
            assert flow_test_method.variable_costs.default \
                   == flow_compare.variable_costs.default
        # compare the investment variables
        if hasattr(flow_test_method, "investment"):
            invest_test_method = flow_test_method.investment
            invest_compare = flow_compare.investment
            if flow_compare.investment:
                assert invest_test_method.ep_costs \
                       == invest_compare.ep_costs
                assert invest_test_method.periodical_constraint_costs \
                       == invest_compare.periodical_constraint_costs
                assert invest_test_method.minimum \
                       == invest_compare.minimum
                assert invest_test_method.maximum \
                       == invest_compare.maximum
                assert invest_test_method.existing \
                       == invest_compare.existing
                assert invest_test_method.nonconvex \
                       == invest_compare.nonconvex
                assert invest_test_method.offset \
                       == invest_compare.offset
                assert invest_test_method.fix_constraint_costs \
                       == invest_compare.fix_constraint_costs
                
                
def comparison_of_flow_attributes(nodes, test_nodes):
    """
    
    """
    # test if the two nodes labels are equal
    assert nodes[0].label == test_nodes[-1].label
    # check if the variable costs and emission factors of the
    # inputs / outputs of the two nodes are equal
    for flows in [nodes[0].inputs, nodes[0].outputs]:
        if flows == nodes[0].inputs:
            flows_test = test_nodes[-1].inputs
        else:
            flows_test = test_nodes[-1].outputs
        assert len(flows) == len(flows_test)
        
        compare_flow_attributes(flows, flows_test)


def import_standard_parameter_data(label: str):
    """
        Method for the import of the test intern version of the
        standard parameter sheet.
        
        :param label: string defining the sheet of the standard \
            parameter sheet which will be loaded and returned to the \
            calling method.
        :type label: str
        :return: - **-** (pandas.DataFrame): Sheet's content which has \
            been loaded within this method.
    """
    standard_parameters = get_standard_parameter_data()
    
    return standard_parameters.parse(label, na_filter=False)


def get_standard_parameter_data() -> pandas.ExcelFile:
    """
        Getter Method to load the standard parameter data.
    
        :return: - **-** (pandas.ExcelFile): dictionary containing the \
            standard parameter data
    """
    # import standard parameter
    return pandas.ExcelFile(os.path.dirname(__file__)
                            + "/standard_parameters.xlsx")