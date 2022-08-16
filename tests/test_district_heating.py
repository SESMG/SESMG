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
