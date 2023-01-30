import pytest


@pytest.fixture
def test_bus_entry():
    """
        A plain oemof model is created, which contains the three
        necessary components (bus, excess sink and shortage source).
        Here, the expected prices are entered as variable costs,
        i.e. euros per kilowatt hour, and the expected emissions as
        grams of CO2 equivalent per kilowatt hour.
    """
    from oemof.solph import EnergySystem, Bus, Sink, Flow, Source
    test_energy_system = EnergySystem()
    # add bus to test energy system
    bus = Bus(label="test_bus")
    test_energy_system.add(bus)
    # add excess sink to test energy system
    test_energy_system.add(Sink(label="test_bus_excess",
                                inputs={bus: Flow(variable_costs=-0.35,
                                                  emission_factor=-27)}))
    # add shortage source to test energy system
    test_energy_system.add(Source(label="test_bus_shortage",
                                  outputs={bus: Flow(variable_costs=0.5,
                                                     emission_factor=300)}))

    return test_energy_system.nodes


@pytest.skip
def test_buses(test_bus_entry):
    """
        Now the Pandas DataFrame structure of the Buses method is
        emulated. For this, on the one hand an active bus:
    
            - shortage: active, 0.5€/kWh, 300 g/kWh
            - excess: active, -0.35€/kWh, -27 g/kWh
    
        and on the other hand a deactivated bus:
    
            - shortage: active, 0.5€/kWh, 300 g/kWh
            - excess: active, -0.35€/kWh, -27 g/kWh
    
        inserted.
    
        Finally, it is checked whether the values can be found again in
        the correct places of the oemof components.
    """
    from .conftest import comparison_of_flow_attributes
    from program_files.preprocessing.components import Bus
    import pandas
    
    nodes_data = {"buses": pandas.DataFrame.from_dict({
        "label": ["test_bus", "test_bus_inactive"],
        "active": [1, 0],
        "excess": [1] * 2,
        "shortage": [1] * 2,
        "excess costs": [-0.35] * 2,
        "shortage costs": [0.5] * 2,
        "excess constraint costs": [-27] * 2,
        "shortage constraint costs": [300] * 2
    })}
    
    nodes = []
    
    busd = Bus.buses(nodes_data=nodes_data, nodes=nodes)
    
    for num in range(len(nodes)):
        # test if the two nodes labels are equal
        assert nodes[num].label == test_bus_entry[num].label
        # check if the variable costs and emission factors of the
        # inputs / outputs of the two nodes are equal
        comparison_of_flow_attributes([nodes[num]], [test_bus_entry[num]])
                
        assert type(busd["test_bus"]) == type(test_bus_entry[0])
