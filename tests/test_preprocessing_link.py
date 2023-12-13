import pytest
import pandas


@pytest.fixture
def test_link_nodes_data():
    """
        Within this fixture the pandas DataFrame used to emulate the
        users model definition input is created.
    """
    return {"links": pandas.DataFrame.from_dict({
            "label": ["test_link", "test_link2"],
            "active": [1, 1],
            "(un)directed": ["directed", "undirected"],
            "bus1": ["test_input_bus"] * 2,
            "bus2": ["test_output_bus"] * 2,
            "variable output costs": [10] * 2,
            "variable output constraint costs": [20] * 2,
            "periodical costs": [30] * 2,
            "periodical constraint costs": [40] * 2,
            "min. investment capacity": [0] * 2,
            "max. investment capacity": [50] * 2,
            "existing capacity": [0] * 2,
            "non-convex investment": [0, 1],
            "fix investment costs": [0, 60],
            "fix investment constraint costs": [0, 70],
            "efficiency": [1] * 2
            })}


@pytest.fixture
def test_directed_convex_link_entry():
    """
        A plain oemof model is created, which contains the three
        necessary components (input bus, output bus and link).
        Here, the expected prices are entered as variable costs,
        i.e. euros per kilowatt hour, and the expected emissions as
        grams of CO2 equivalent per kilowatt hour.
    """
    from oemof.solph.buses import Bus
    from oemof.solph import EnergySystem, Investment
    from oemof.solph.flows import Flow
    from oemof.solph.components.experimental import Link
    test_energy_system = EnergySystem()
    # add bus to test energy system
    input_bus = Bus(label="test_input_bus")
    test_energy_system.add(input_bus)
    output_bus = Bus(label="test_output_bus")
    test_energy_system.add(output_bus)
    # add excess sink to test energy system
    link = Link(
        label="test_link",
        inputs={input_bus: Flow(variable_costs=0,
                                custom_attributes={"emission_factor": 0}),
                # necessary for component creation but deleted
                # afterwards
                output_bus: Flow()},
        outputs={
            # necessary for component creation but deleted
            # afterwards
            input_bus: Flow(),
            output_bus: Flow(
                variable_costs=10,
                custom_attributes={"emission_factor": 20},
                investment=Investment(
                    ep_costs=30,
                    minimum=0,
                    maximum=50,
                    existing=0,
                    nonconvex=False,
                    offset=0,
                    custom_attributes={"periodical_constraint_costs": 40,
                                       "fix_constraint_costs": 0}
                 ))},
        conversion_factors={(input_bus, output_bus): 1,
                            (output_bus, input_bus): 1})

    # delete the not used direction
    link.inputs.pop(output_bus)
    link.outputs.pop(input_bus)
    link.conversion_factors.pop((output_bus, input_bus))
    
    test_energy_system.add(link)
    
    return test_energy_system.nodes


@pytest.fixture
def test_undirected_non_convex_link_entry():
    """
        A plain oemof model is created, which contains the three
        necessary components (input bus, output bus and link).
        Here, the expected prices are entered as variable costs,
        i.e. euros per kilowatt hour, and the expected emissions as
        grams of CO2 equivalent per kilowatt hour.
    """
    from oemof.solph.buses import Bus
    from oemof.solph import EnergySystem, Investment
    from oemof.solph.flows import Flow
    from oemof.solph.components.experimental import Link
    test_energy_system = EnergySystem()
    # add bus to test energy system
    input_bus = Bus(label="test_input_bus")
    test_energy_system.add(input_bus)
    output_bus = Bus(label="test_output_bus")
    test_energy_system.add(output_bus)
    # add excess sink to test energy system
    link = Link(
        label="test_link2",
        inputs={input_bus: Flow(variable_costs=0,
                                custom_attributes={"emission_factor": 0}),
                output_bus: Flow(variable_costs=0,
                                 custom_attributes={"emission_factor": 0})},
        outputs={
            input_bus: Flow(
                variable_costs=10,
                custom_attributes={"emission_factor": 20},
                investment=Investment(
                    ep_costs=30 / 2,
                    minimum=0,
                    maximum=50,
                    existing=0,
                    nonconvex=True,
                    offset=60 / 2,
                    custom_attributes={"periodical_constraint_costs": 40 / 2,
                                       "fix_constraint_costs": 70 / 2}
                )),
            output_bus: Flow(
                variable_costs=10,
                custom_attributes={"emission_factor": 20},
                investment=Investment(
                    ep_costs=30 / 2,
                    minimum=0,
                    maximum=50,
                    existing=0,
                    nonconvex=True,
                    offset=60 / 2,
                    custom_attributes={"periodical_constraint_costs": 40 / 2,
                                       "fix_constraint_costs": 70 / 2},
                ))},
        conversion_factors={(input_bus, output_bus): 1,
                            (output_bus, input_bus): 1})

    test_energy_system.add(link)
    return test_energy_system.nodes


def test_get_flow(test_link_nodes_data,
                  test_undirected_non_convex_link_entry):
    """
        This test is used to test the static method of the link class,
        in which the parameterization of the output flow of the link
        component has been outsourced. For this purpose, the output of
        the undirected non-convex link is used.
    
    """
    from .conftest import compare_flow_attributes
    from program_files.preprocessing.components.Link import Links
    from oemof.solph import Bus
    # get the links data frame from the nodes data structure (fixture)
    links_df = test_link_nodes_data["links"]
    # iterate threw the data frame
    for num, link in links_df.iterrows():
        # search for the data frame entry to be tested
        if link["label"] == "test_link2":
            # start the method to be tested
            flow = Links.get_flow(link=link)
            # compare the oemof Flow's attributes
            compare_flow_attributes(
                flows={Bus(label="test_output_bus"): flow},
                flows_test=test_undirected_non_convex_link_entry[-1].outputs)
        
    
def test_links(test_link_nodes_data,
               test_directed_convex_link_entry,
               test_undirected_non_convex_link_entry):
    """
        Now the Pandas DataFrame structure of the Links method is
        emulated. For this, on the one hand an convex directed link:

            - active
            - directed
            - variable output costs 10 €/kWh
            - variable output constraint costs 20 g/kWh
            - periodical costs 30 €/(kW * a)
            - periodical constraint costs 40 g/(kW * a)
            - min. investment capacity 0 kW
            - max. investment capacity 50 kW
            - existing capacity 0 kW
            - convex
            - efficiency 1

        and on the other hand a non-convex undirected link:

            - active
            - undirected
            - variable output costs 10 €/kWh
            - variable output constraint costs 20 g/kWh
            - periodical costs 15 €/(kW * direction * a)
            - periodical constraint costs 20 g/(kW * direction * a)
            - min. investment capacity 0 kW
            - max. investment capacity 50 kW
            - existing capacity 0 kW
            - non-convex
            - fix investment costs 30 €/(direction * a)
            - fix investment constraint costs 35 g/(direction * a)
            - efficiency 1

        inserted.

        Finally, it is checked whether the values can be found again in
        the correct places of the oemof components.
    """
    from .conftest import comparison_of_flow_attributes
    from program_files.preprocessing.components import Link, Bus
    import pandas
    
    # create dummy buses which are not part of the test but necessary
    # for the creation of the links
    bus_data = {"buses": pandas.DataFrame.from_dict({
        "label": ["test_input_bus", "test_output_bus"],
        "active": [1] * 2,
        "excess": [0] * 2,
        "shortage": [0] * 2,
        "excess costs": [0] * 2,
        "shortage costs": [0] * 2,
        "excess constraint costs": [0] * 2,
        "shortage constraint costs": [0] * 2
    })}
    
    busd, nodes = Bus.buses(nd_buses=bus_data["buses"], nodes=[])
    
    Link.Links(nodes_data=test_link_nodes_data, nodes=nodes, busd=busd)
    
    # check rather the links' parameter are assigned correctly
    comparison_of_flow_attributes(
        nodes=[nodes[2]],
        test_link_entry=test_directed_convex_link_entry)
    
    comparison_of_flow_attributes(
        nodes=[nodes[3]],
        test_link_entry=test_undirected_non_convex_link_entry)
