import pytest
import pandas
import dhnx
import dhnx.optimization.oemof_heatpipe as heatpipe
from oemof import solph
from program_files.preprocessing.components import district_heating_components


@pytest.fixture
def thermal_net():
    """
        Fixture to create a new ThermalNetwork instance for each test.
    """
    return dhnx.network.ThermalNetwork()


@pytest.fixture
def test_forks_dataframe():
    """
        The pandas dataframe created here provides the benchmark for
        test_concat_on_thermal_net_components and test_create_fork.
    """
    return pandas.DataFrame.from_dict(
        {"id": [1],
         "lat": [10],
         "lon": [10],
         "component_type": ["Fork"],
         "street": ["test"],
         "t": [0.5],
         "bus": ["testbus"]}
    )


def test_create_fork(test_forks_dataframe, thermal_net):
    """
        This test checks whether the row created by the create fork
        method has been correctly parameterized in the DataFrame of the
        thermal network forks.
    """
    # Creating an instance of the ThermalNetwork
    # Assuming create_fork is a method of the district_heating module
    # and it adds a new fork to the thermal network
    # with the specified parameters (point, label, bus)
    point = ["x", 10, 10, "x", 0.5, "test"]
    label = 1
    bus = "testbus"
    
    # Calling the create_fork method to add a new fork to the thermal
    # network
    thermal_net = district_heating_components.create_fork(
            point=point,
            label=label,
            thermal_net=thermal_net,
            bus=bus)
    
    # Comparing the resulting 'forks' component DataFrame with the
    # expected test dataframe
    pandas.testing.assert_frame_equal(
            left=thermal_net.components["forks"],
            right=test_forks_dataframe
    )


@pytest.fixture
def test_pipes_dataframe():
    """
        The pandas dataframe created here provides the benchmark for
        test_append_pipe.
    """
    return pandas.DataFrame.from_dict(
            {"id": ["pipe-1"],
             "from_node": ["forks-1"],
             "to_node": ["forks-2"],
             "length": [30.0],
             "component_type": ["Pipe"],
             "street": ["test-street"],
             "is_exergy": [True]}
    )


def test_append_pipe(test_pipes_dataframe, thermal_net):
    """
        This test checks whether the row created by the append pipe
        method has been correctly parameterized in the DataFrame of the
        thermal network pipes.
    """
    # Creating an instance of the ThermalNetwork
    # Assuming append_pipe is a method of the district_heating module
    # and it adds a new pipe to the thermal network
    # with the specified parameters (nodes, length, street)
    nodes = ["forks-1", "forks-2"]
    length = 30.0
    street = "test-street"
    
    # Calling the append_pipe method to add a new pipe to the thermal
    # network
    thermal_net = district_heating_components.append_pipe(
            nodes=nodes,
            length=length,
            street=street,
            thermal_net=thermal_net,
            is_exergy=True)
    
    # Comparing the resulting 'pipes' component DataFrame with the
    # expected test dataframe
    pandas.testing.assert_frame_equal(
            left=thermal_net.components["pipes"],
            right=test_pipes_dataframe
    )
    

def test_create_connection_points():
    """
        TODO
    """
    pass


@pytest.fixture
def street_sec():
    return pandas.DataFrame({
        'active': [1, 1],
        'lat. 1st intersection': [1.0, 2.0],
        'lon. 1st intersection': [3.0, 4.0],
        'lat. 2nd intersection': [5.0, 6.0],
        'lon. 2nd intersection': [7.0, 8.0]
    })


def test_create_intersection_forks(street_sec, thermal_net):
    """
        Test the create_intersection_forks function.

        This test function checks the behavior of the
        create_intersection_forks method by providing it with specific
        street_sec and thermal_net inputs and then asserting the
        expected behavior and properties of the resulting
        ThermalNetwork instance.

        :param: street_sec: Test DataFrame containing street \
          sections with beginning and ending points.
        :type street_sec: pandas.DataFrame
        :param thermal_net: Test instance of the DHNx ThermalNetwork \
          used as a basis for creating the components.
        :type street_sec: dhnx.network.ThermalNetwork
        """
    # Call the method with the test data
    result_thermal_net = district_heating_components.create_intersection_forks(
            street_sec=street_sec, thermal_net=thermal_net)
    
    # Assert the result is an instance of ThermalNetwork
    assert isinstance(result_thermal_net, dhnx.network.ThermalNetwork)
    
    # Check if the forks component is updated
    assert len(result_thermal_net.components["forks"]) == 4
    
    # Check if the properties of the forks are as expected
    forks = result_thermal_net.components["forks"]
    assert sorted(forks["lat"].to_list()) == [1.0, 2.0, 5.0, 6.0]
    assert sorted(forks["lon"].to_list()) == [3.0, 4.0, 7.0, 8.0]
    

class MockThermalNetwork2:
    def __init__(self, forks, pipes, consumers):
        self.components = {"forks": forks,
                           "pipes": pipes,
                           "consumers": consumers}


@pytest.fixture
def sample_points_data():
    return MockThermalNetwork2(
            forks=pandas.DataFrame(data={
                "lat": [5.0, 10.0, 20.0, 12.0, 22.0],
                "lon": [2.0, 15.0, 25.0, 18.0, 28.0],
                "id": ["consumers-1", "forks-1", "forks-2", "forks-3",
                       "forks-4"],
                "t": ["", 0, 0.25, 0.5, 0.75]
            }),
            pipes=pandas.DataFrame(data={}),
            consumers=None
    )


@pytest.fixture
def sample_streets_data():
    data = {
        "label": ["street1", "street2"],
        "active": [1, 1],
        "lat. 1st intersection": [10.0, 20.0],
        "lon. 1st intersection": [15.0, 25.0],
        "lat. 2nd intersection": [12.0, 22.0],
        "lon. 2nd intersection": [18.0, 28.0],
    }
    return pandas.DataFrame(data)


def test_create_supply_line(sample_streets_data, sample_points_data):
    # Call the method with sample data
    result_thermal_net = district_heating_components.create_supply_line(
            streets=sample_streets_data,
            thermal_net=sample_points_data,
            is_exergy=True)
    
    pipes = result_thermal_net.components["pipes"]
    # Check if pipes where added to the thermal network pipes dataframe
    assert len(pipes) > 0
    
    # Check if forks-1 -- a from node -- is listed in from node column
    assert "forks-forks-1" in pipes["from_node"].to_list()
    # Check if length of pipe 1 is listed in length column
    assert 396208.1053375902 in pipes["length"].to_list()
    # Check if forks-3 -- a to node -- is listed in to node column
    assert "forks-forks-3" in pipes["to_node"].to_list()
    
    
class MockOemofOptiModel:
    def __init__(self, buses, nodes):
        self.nodes = nodes
        self.buses = buses
    
    
def test_create_producer_connection():
    """
        Test case for the create_producer_connection method.

        This test checks if the create_producer_connection method
        correctly adds a Transformer component to the
        OemofInvestOptimizationModel nodes when connecting a heat
        producer to the thermal network.
    
        The method is tested with a mock OemofInvestOptimizationModel,
        a mock ThermalNetwork, and a dictionary of buses.
    
        Assertions:
        1. The number of nodes in the resulting
           OemofInvestOptimizationModel is 1.
        2. The type of the added node is a
           solph.components.Transformer.
        3. The string representation of the added node matches the
           expected value.
    """
    # Create a mock OemofInvestOptimizationModel with a heat bus
    oemof_opti_model = MockOemofOptiModel(
        buses={
            heatpipe.Label(
                "producers", "heat", "bus", "producers-0", "exergy"):
            solph.buses.Bus(label="producers_heat_bus_0_exergy")},
        nodes=[]
    )

    # Create a mock ThermalNetwork with a fork
    thermal_net = MockThermalNetwork2(
            forks=pandas.DataFrame(data={
                "bus": ["heat_input1"]
            }),
            pipes=None,
            consumers=None)
    
    # Create a dictionary of buses
    busd = {"heat_input1": solph.buses.Bus(label="heat_input1")}
    
    # Call the method
    result = district_heating_components.create_producer_connection(
        oemof_opti_model=oemof_opti_model,
        busd=busd,
        label_5="exergy",
        thermal_net=thermal_net)

    # Assertions
    assert len(result.nodes) == 1
    assert type(result.nodes[0]) == solph.components.Converter
    assert str(result.nodes[0]) == "heat_input1_dh_source_link_exergy"


def test_connect_dh_to_system_exergy():
    """
        Test the 'connect_dh_to_system' method from the
        'district_heating_components' module.
    
        The test checks whether the method correctly updates the
        OemofInvestOptimizationModel and the bus dictionary when
        connecting consumers to the thermal network.
    
        Assertions:
        1. The number of nodes in the resulting
           OemofInvestOptimizationModel is 2.
        2. The heat house station is within these nodes.
        3. The consumers heat bus has been added to the busd dict.
    """
    # Create a mock OemofInvestOptimizationModel
    oemof_opti_model = MockOemofOptiModel(
        buses={
            heatpipe.Label(
                "consumers", "heat", "bus", "consumers-0", "exergy"):
            solph.buses.Bus(label="consumers_heat_bus_0_exergy")},
        nodes=[solph.Bus(label="consumers_heat_bus_consumers-0_exergy")])
    
    # Create a mock ThermalNetwork
    thermal_net = MockThermalNetwork2(
            consumers=pandas.DataFrame(data={
                "id": [0],
                "input": ["input_1"],
                "label": ["Testhouse_heat_bus"],
                "active": [1],
                "existing heathouse station": [0]
            }),
            pipes=None,
            forks=None
    )
    
    # Create a dictionary of buses
    busd = {"input_1": solph.buses.Bus(label="input_1")}
    
    # Create a DataFrame for pipe types
    pipe_types = pandas.DataFrame(data={
        "label_3": ["dh_heatstation"],
        "capex_pipes": [100],
        "periodical_constraint_costs": [10],
        "efficiency": [0.9]
    })
    
    # Call the method
    result, updated_busd = \
        district_heating_components.connect_dh_to_system_exergy(
            oemof_opti_model=oemof_opti_model,
            busd=busd,
            pipe_types=pipe_types,
            thermal_net=thermal_net
    )
    
    # Assert the changes in the oemof_opti_model
    assert len(result.nodes) == 2
    assert type(result.nodes[1]) == solph.components.Converter
    assert str(result.nodes[1]) == \
        "dh_heat_house_station_Testhouse_heat_bus"
    
    # Assert the changes in the bus dictionary
    assert len(updated_busd) == 2
    assert "consumers_heat_bus_consumers-0_exergy" in updated_busd
    assert updated_busd[
               "consumers_heat_bus_consumers-0_exergy"].label == \
           "consumers_heat_bus_consumers-0_exergy"
    assert "input_1" in updated_busd
    assert updated_busd["input_1"].label == "input_1"


def test_create_link_between_dh_heat_bus_and_excess_shortage_bus():
    """
        Test the creation of a link between the district heating heat
        bus and the excess/shortage bus.

        This test ensures that the created link has the correct
        properties and connections.
    """
    # Define a mock bus dictionary
    busd = {"bus1": solph.buses.Bus(label="bus1")}

    # Define a mock bus Series
    bus = pandas.Series({"label": "bus1"})

    # Define a mock fork label
    fork_label = heatpipe.Label("", "", "", "forks-0", "")

    # Create a mock OemofOptiModel
    oemof_opti_model = MockOemofOptiModel(
        buses={fork_label: solph.buses.Bus(label="forks-1")},
        nodes={}
    )
    
    # Call the method
    result = district_heating_components.create_link_between_dh_heat_bus_and_excess_shortage_bus(
        busd=busd,
        bus=bus,
        oemof_opti_model=oemof_opti_model,
        fork_label=fork_label
    )

    # Assert the link properties
    assert result.label.startswith("link-dhnx-bus1-f0")
    assert result.inputs[oemof_opti_model.buses[fork_label]
                         ].emission_factor == 0
