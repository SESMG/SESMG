import pytest
import pandas
import os


@pytest.fixture
def test_storage_decentralized_battery_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    storages = standard_parameters.parse("5_storages")
    storage = storages.loc[storages["storage_type"]
                           == "building_battery_storage"]
    # combine specific data and the standard parameter data
    sheets = {
        "storages":
            pandas.merge(
                    left=pandas.DataFrame.from_dict({
                        "label": ["test_building_battery_storage"],
                        "storage_type": ["building_battery_storage"],
                        "bus": ["test_building_electricity_bus"]}),
                    right=storage,
                    left_on="storage_type",
                    right_on="storage_type"
            )}

    # remove column which was used to merge the two dataframe parts
    sheets["storages"] = sheets["storages"].drop(columns=["storage_type"])

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
                
                
def comparison_of_flow_attributes(nodes, test_link_entry):
    """
    
    """
    # test if the two nodes labels are equal
    assert nodes[0].label == test_link_entry[-1].label
    # check if the variable costs and emission factors of the
    # inputs / outputs of the two nodes are equal
    for flows in [nodes[0].inputs, nodes[0].outputs]:
        if flows == nodes[0].inputs:
            flows_test = test_link_entry[-1].inputs
        else:
            flows_test = test_link_entry[-1].outputs
        assert len(flows) == len(flows_test)
        
        compare_flow_attributes(flows, flows_test)
