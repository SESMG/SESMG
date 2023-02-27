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
