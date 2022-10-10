import pytest
from program_files.preprocessing.components.district_heating_calculations import (
    calc_perpendicular_distance_line_point,
    transf_WGS84_GK,
)


def test_perpendicular_foot_print_calc():
    p1 = transf_WGS84_GK.transform(1, 1)
    p2 = transf_WGS84_GK.transform(2, 1)
    test_list = calc_perpendicular_distance_line_point(p1, p2, [1.5, 1.5])
    assert 1.5 == pytest.approx(test_list[0], 1e-4)
    assert 1 == pytest.approx(test_list[1], 1e-3)
    assert 55600 == pytest.approx(test_list[2], 1e-1)
    assert 0.5 == pytest.approx(test_list[3], 1e-3)
    

def test_create_fork():
    from program_files.preprocessing.components.district_heating \
        import create_fork
    import dhnx
    thermal_net = dhnx.network.ThermalNetwork()
    create_fork(["x", 10, 10, "x", 0.5, "test"], 1, thermal_net, "testbus")
    assert 10 == int(thermal_net.components["forks"]["lat"])
    assert 10 == int(thermal_net.components["forks"]["lon"])
    assert 0.5 == float(thermal_net.components["forks"]["t"])
    assert "test" == str(thermal_net.components["forks"]["street"][0])
    assert "testbus" == str(thermal_net.components["forks"]["bus"][0])


def test_append_pipe():
    from program_files.preprocessing.components.district_heating \
        import append_pipe
    import dhnx
    thermal_net = dhnx.network.ThermalNetwork()
    append_pipe("forks-1", "forks-2", 30.0, "test-street", thermal_net)
    assert "forks-1" == str(thermal_net.components["pipes"]["from_node"][0])
    assert "forks-2" == str(thermal_net.components["pipes"]["to_node"][0])
    assert 30.0 == float(thermal_net.components["pipes"]["length"])
    assert "test-street" == str(thermal_net.components["pipes"]["street"][0])