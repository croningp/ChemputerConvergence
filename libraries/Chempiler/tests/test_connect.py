import os
import pytest
from chempiler import Chempiler
import ChemputerAPI
from networkx.exception import NetworkXNoPath

HERE = os.path.abspath(os.path.dirname(__file__))
GRAPH_FOLDER = os.path.join(HERE, 'graph_files')

tests = [
    # Flask nitrogen to filter through three valves, ports specified
    (
        'three_valve_connect.json',
        ('flask_nitrogen', 'filter', 0, 'bottom'),
        [
            ('valve1', ('route', -1, 1)),
            ('valve2', ('route', -1, 2)),
            ('valve3', ('route', -1, 3)),
        ],
    ),

    # Flask nitrogen to filter through three valves, no ports specified
    (
        'three_valve_connect.json',
        ('flask_nitrogen', 'filter', None, None),
        [
            ('valve1', ('route', -1, 1)),
            ('valve2', ('route', -1, 2)),
            ('valve3', ('route', -1, 3)),
        ],
    ),

    # Flask nitrogen to filter through vacuum valve, ports specified
    (
        'AlkylFluor_full.graphml',
        ('flask_nitrogen', 'jacketed_filter', 0, 'bottom'),
        [
            ('valve_vacuum', ('route', 2, -1)),
        ],
    ),

    # Flask nitrogen to filter through vacuum valve, no ports specified
    (
        'AlkylFluor_full.graphml',
        ('flask_nitrogen', 'jacketed_filter', None, None),
        [
            ('valve_vacuum', ('route', 2, -1)),
        ],
    ),

    # Flask vacuum to filter through vacuum valve, ports specified
    (
        'AlkylFluor_full.graphml',
        ('flask_vacuum', 'jacketed_filter', 0, 'bottom'),
        [
            ('valve_vacuum', ('route', 5, -1)),
        ],
    ),

    # Flask vacuum to filter through vacuum valve, no ports specified
    (
        'AlkylFluor_full.graphml',
        ('flask_vacuum', 'jacketed_filter', None, None),
        [
            ('valve_vacuum', ('route', 5, -1)),
        ],
    ),

    # Flask vacuum to filter through vacuum valve, ports specified
    (
        'bigrig.json',
        ('vacuum_flask', 'filter', 0, 'bottom'),
        [
            ('valve_vacuum', ('route', 0, -1)),
        ],
    ),

    # Flask vacuum to filter through vacuum valve, no ports specified
    (
        'bigrig.json',
        ('vacuum_flask', 'filter', None, None),
        [
            ('valve_vacuum', ('route', 0, -1)),
        ],
    ),

    # Flask vacuum to rotavap through backbone, should fail, ports specified.
    (
        'AlkylFluor_full.graphml',
        ('flask_nitrogen', 'rotavap', 0, 'evaporate'),
        None,
    ),

    # Flask nitrogen through three valves with one connected not through -1,
    # should fail.
    (
        'three_valve_connect_bad_ports.json',
        ('flask_nitrogen', 'filter', 0, 'bottom'),
        None,
    ),
]

def test_connect():
    """Test that connect method finds right steps to execute."""
    for graph, target, label_operations in tests:

        # Get target nodes to find path for
        src_port, dest_port = None, None
        if len(target) == 4:
            src, dest, src_port, dest_port = target
        elif len(target) == 2:
            src, dest = target

        # Instantiate Chempiler from graph
        c = Chempiler(experiment_code="test",
                      output_dir="out",
                      simulation=True,
                      graph_file=os.path.join(GRAPH_FOLDER, graph),
                      device_modules=[ChemputerAPI])

        # Path shouldn't be found, check that no false positive paths are found.
        if label_operations is None:
            with pytest.raises(NetworkXNoPath):
                operations = c.connect(src, dest, src_port, dest_port)

        # Path should be found, check that correct operations are being carried
        # out.
        else:
            operations = c.connect(src, dest, src_port, dest_port)
            assert len(operations) == len(label_operations)
            for i in range(len(operations)):
                assert operations[i] == label_operations[i]
