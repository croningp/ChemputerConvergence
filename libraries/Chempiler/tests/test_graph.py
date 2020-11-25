import os
import sys
import pytest
import logging

import ChemputerAPI
from networkx.exception import NetworkXNoPath
from chempiler.tools.graph import ChempilerGraph

# Paths
HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH_FILE = os.path.join(HERE, "graph_files", "DMP_graph_test.json")
ROOT = os.path.join(HERE, "..", "..")
sys.path.append(ROOT)

# Logger
logger = logging.getLogger("test_graph")

# Set up the graph
graph = ChempilerGraph(GRAPH_FILE, logger, [ChemputerAPI], simulation=True)

def test_optimal_path():
    # Expected results
    expected = [
        [
            "flask_oxone_aq",
            "valve_filter",
            "valve_dry",
            "valve_organic",
            "valve_separator",
            "valve_rotavap",
            "rotavap"
        ],
        [
            "flask_argon",
            "valve_dry",
            "valve_filter",
            "filter1"
        ],
        [
            "flask_argon",
            "valve_dry",
            "valve_filter",
            "valve_vacuum",
            "filter1"
        ]
    ]

    # Find paths for the three cases
    p1 = graph.find_optimal_path("flask_oxone_aq", "rotavap")
    p1 = [step.src for step in p1] + [p1[-1].dest]

    p2 = graph.find_optimal_path("flask_argon", "filter1", dest_port="top")
    p2 = [step.src for step in p2] + [p2[-1].dest]

    p3 = graph.find_optimal_path(
        "flask_argon", "filter1", dest_port="bottom", use_backbone=False)
    p3 = [step.src for step in p3] + [p3[-1].dest]

    print(p3)
    # Assert they equal the expected
    assert p1 == expected[0]
    assert p2 == expected[1]
    assert p3 == expected[2]


def test_backbone():
    # Expected result
    expected = [
        "valve_filter",
        "valve_dry",
        "valve_organic",
        "valve_separator",
        "valve_rotavap",
        "valve_workup"
    ]

    # Check length of backbone matches expected
    assert len(expected) == len(graph.backbone)

    # Assert each expected valve is int he backbone
    for elem in expected:
        assert elem in graph.backbone

def test_through_path():
    # Expected path through drying cartridge
    expected_drying = [
        ["flask_oxone_aq", "valve_filter", (0, 1)],
        ["valve_filter", "valve_dry", (4, 5)],
        ["valve_dry", "valve_organic", (4, 5)],
        ["valve_organic", "valve_separator", (4, 5)],
        ["valve_separator", "cartridge_drying", (1, "in")],
        ["cartridge_drying", "valve_rotavap", ("out", 1)],
        ["valve_rotavap", "rotavap", (3, "evaporate")]
    ]

    # Expected path through separator and drying
    expected_separator = [
        [
            ["flask_oxone_aq", "valve_filter", (0, 1)],
            ["valve_filter", "valve_dry", (4, 5)],
            ["valve_dry", "valve_organic", (4, 5)],
            ["valve_organic", "valve_separator", (4, 5)],
            ["valve_separator", "flask_separator", (3, "bottom")]
        ],
        [
            ["flask_separator", "valve_separator", ("bottom", 3)],
            ["valve_separator", "cartridge_drying", (1, "in")],
            ["cartridge_drying", "valve_rotavap", ("out", 1)],
            ["valve_rotavap", "rotavap", (3, "evaporate")]
        ]
    ]

    # Check they match
    p = graph.find_path("flask_oxone_aq", "rotavap", through="cartridge_drying")
    for i, step in enumerate(p):
        assert step.as_tuple() == tuple(expected_drying[i])

    # Check they match
    p = graph.find_path(
        "flask_oxone_aq",
        "rotavap",
        through=["flask_separator", "cartridge_drying"]
    )
    print(*p)
    for i, step_list in enumerate(p):
        for j, step in enumerate(step_list):
            assert step.as_tuple() == tuple(expected_separator[i][j])

def test_using_backbone():
    # Expected result using backbone
    with_backbone = [
        ["flask_ether_anhydrous", "valve_dry", (0, 2)],
        ["valve_dry", "valve_filter", (5, 4)],
        ["valve_filter", "filter1", (3, "top")]
    ]

    # Get the path
    pwb = graph.find_path(
        "flask_ether_anhydrous",
        "filter1",
        dest_port="top"
    )

    # Check they match
    for i, step in enumerate(pwb):
        assert step.as_tuple() == tuple(with_backbone[i])

    # No path error caught
    with pytest.raises(NetworkXNoPath):
        print('THROUGH TEST')
        print(graph.find_path(
            "flask_ether_anhydrous",
            "filter1",
            dest_port="top",
            through="valve_vacuum",
            use_backbone=False
        ))

def test_all_pumps_are_present():
    # Expected pumps in the graph
    expected_pumps = [
        "pump_filter",
        "pump_dry",
        "pump_air",
        "pump_workup",
        "pump_rotavap",
        "pump_cartridge"
    ]

    # List of all valves
    valve_list = [
        v for v in graph.nodes
        if graph[v]["class"] == "ChemputerValve"
    ]

    # Get all pump names
    pump_list = []
    for valve in valve_list:
        pump = graph.get_pump_from_valve_name(valve)
        if pump:
            pump_list.append(pump.name)

    # Check the total is equal
    assert len(pump_list) == len(expected_pumps)

    # Check each pump is present
    for pump in pump_list:
        assert pump in expected_pumps

def test_invalid_valve_paths():
    # Ensures all paths from a flask to valve cannot be reversed
    with pytest.raises(NetworkXNoPath):
        graph.find_path("valve_filter", "flask_water")
        graph.find_path("valve_dry", "flask_argon")
        graph.find_path("valve_organic", "flask_acetone")
        graph.find_path("waste_workup", "valve_separator")
        graph.find_path("waste_rotavap", "valve_rotavap")
        graph.find_path("valve_workup", "flask_bicarbonate")

def test_invalid_paths():
    # Ensures that these paths are not valid paths
    with pytest.raises(NetworkXNoPath):
        graph.find_path(
            "flask_ether_anhydrous",
            "filter1",
            through="valve_vacuum",
            dest_port="bottom"
        )

        graph.find_path("flask_menthol", "flask_water")
        graph.find_path(
            "flask_bicarbonate", "flask_bicarbonate", through="rotavap"
        )
