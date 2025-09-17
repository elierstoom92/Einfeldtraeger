from __future__ import annotations

import math

import pytest

from einfeldtraeger.beam import PointLoad, SimplySupportedBeam
from einfeldtraeger.diagram import render_diagram


def test_reactions_with_distributed_load_only():
    beam = SimplySupportedBeam(length=6.0, distributed_load=5.0)
    assert pytest.approx(beam.reaction_left) == 15.0
    assert pytest.approx(beam.reaction_right) == 15.0

    xs, shear, moment = beam.evaluate(points=3)
    assert xs == [0.0, 3.0, 6.0]
    assert pytest.approx(shear) == [15.0, 0.0, -15.0]
    assert pytest.approx(moment) == [0.0, 22.5, 0.0]


def test_reactions_with_point_load():
    load = PointLoad(magnitude=10.0, position=2.0)
    beam = SimplySupportedBeam(length=5.0, point_loads=[load])
    assert pytest.approx(beam.reaction_left) == pytest.approx(6.0)
    assert pytest.approx(beam.reaction_right) == pytest.approx(4.0)

    xs, shear, moment = beam.evaluate(points=6)
    assert pytest.approx(shear[:3]) == [6.0, 6.0, -4.0]
    assert pytest.approx(moment[2]) == 12.0


def test_combined_loads_superpose():
    load = PointLoad(magnitude=12.0, position=3.0)
    beam = SimplySupportedBeam(length=6.0, distributed_load=2.0, point_loads=[load])
    xs, shear, moment = beam.evaluate(points=4)

    # Reference results from hand calculation
    assert pytest.approx(beam.reaction_left, rel=1e-6) == 12.0
    assert pytest.approx(beam.reaction_right, rel=1e-6) == 12.0
    assert pytest.approx(shear) == [12.0, 8.0, -8.0, -12.0]
    assert pytest.approx(moment[1], rel=1e-6) == 20.0


def test_invalid_positions_raise():
    with pytest.raises(ValueError):
        SimplySupportedBeam(length=5.0, point_loads=[PointLoad(5.0, -1.0)])
    with pytest.raises(ValueError):
        SimplySupportedBeam(length=5.0, point_loads=[PointLoad(5.0, 6.0)])


def test_diagram_renders_zero_line():
    xs = [0.0, 1.0, 2.0]
    values = [-1.0, 0.0, 1.0]
    diagram = render_diagram(xs, values, height=7, width=5)
    lines = diagram.splitlines()
    zero_row = 1 + 7 // 2  # account for top label line
    assert lines[zero_row][0] == "┼"
    assert lines[zero_row][-1] == "┤"


def test_maximum_helpers():
    beam = SimplySupportedBeam(length=8.0, distributed_load=3.0)
    x_s, v = beam.max_shear(points=101)
    x_m, m = beam.max_moment(points=101)

    assert math.isclose(x_s, 0.0, abs_tol=1e-6)
    assert math.isclose(v, 12.0, abs_tol=1e-6)
    assert math.isclose(x_m, 4.0, abs_tol=1e-6)
    assert math.isclose(m, 24.0, abs_tol=1e-6)


