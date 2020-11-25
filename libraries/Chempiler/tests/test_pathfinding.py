import os
import pytest
from chempiler import Chempiler
import ChemputerAPI
from networkx.exception import NetworkXNoPath

HERE = os.path.abspath(os.path.dirname(__file__))
GRAPH_FOLDER = os.path.join(HERE, 'graph_files')

tests = [
    (
        'discovery_graph.json',
        ('clean_solvent_1', 'waste_5', 0, 0),
        [
            [
                ('clean_solvent_1', 'valve_14', (0, 5)),
                ('valve_14', 'valve_2', (-1, 2)),
                ('valve_2', 'pump_52', (-1, 0))
            ],
            [
                ('pump_52', 'valve_2', (0, -1)),
                ('valve_2', 'valve_14', (2, -1)),
                ('valve_14', 'waste_5', (3, 0))
            ],
        ]
    ),
    (
        'discovery_graph.json',
        ('reactor_10', 'waste_7', 0, 0),
        [
            [
                ('reactor_10', 'valve_7', (0, 5)),
                ('valve_7', 'valve_5', (-1, 2)),
                ('valve_5', 'pump_51', (-1, 0))
            ],
            [
                ('pump_51', 'valve_5', (0, -1)),
                ('valve_5', 'valve_7', (2, -1)),
                ('valve_7', 'waste_7', (3, 0))
            ],
        ]
    ),
    (
        'pump_then_valves.json',
        ('flask_nitrogen', 'filter', 0, 'bottom', []),
        [
            ('flask_nitrogen', 'valve1', (0, 2)),
            ('valve1', 'valve2', (1, -1)),
            ('valve2', 'valve3', (2, -1)),
            ('valve3', 'filter', (3, 'bottom'))
        ],
    ),

    (
        'pump_then_valves_bad_ports.json',
        ('flask_nitrogen', 'filter', 0, 'bottom', []),
        None,
    ),

    (
        'bigrig.json',
        ('flask_water', 'waste_separator', 0, 0),
        [
            ('flask_water', 'valve_rotavap', (0, 0)),
            ('valve_rotavap', 'valve_reactor', (5, 4)),
            ('valve_reactor', 'valve_filter', (5, 4)),
            ('valve_filter', 'valve_separator', (5, 4)),
            ('valve_separator', 'waste_separator', (2, 0))
        ],
    ),

    (
        'AlkylFluor_full.graphml',
        ('flask_nitrogen', 'jacketed_filter', 0, 'bottom'),
        [
            ('flask_nitrogen', 'valve_G', (0, 1)),
            ('valve_G', 'valve_F', (2, 1)),
            ('valve_F', 'valve_E', (2, 1)),
            ('valve_E', 'valve_D', (2, 1)),
            ('valve_D', 'valve_C', (2, 1)),
            ('valve_C', 'valve_vacuum', (3, 1)),
            ('valve_vacuum', 'jacketed_filter', (-1, 'bottom'))
        ],
    ),

    (
        'AlkylFluor_full.graphml',
        ('flask_water', 'jacketed_filter', 0, 'top'),
        None,
    ),

    (
        'orgsyn_v83p0193_graph.json',
        ('reactor', 'separator', 0, 'top'),
        None,
    ),

    (
        'AlkylFluor_full.graphml',
        ('flask_THF', 'rotavap', 0, 'evaporate', ['cartridge_celite_C']),
        [
            ('flask_THF', 'valve_G', (0, 3)),
            ('valve_G', 'valve_F', (2, 1)),
            ('valve_F', 'valve_E', (2, 1)),
            ('valve_E', 'valve_D', (2, 1)),
            ('valve_D', 'cartridge_celite_C', (5, 'in')),
            ('cartridge_celite_C', 'manifold', ('out', 0)),
            ('manifold', 'valve_E', (0, 3)),
            ('valve_E', 'valve_F', (1, 2)),
            ('valve_F', 'rotavap', (5, 'evaporate')),
        ],
    ),

    (
        'lidocaine_graph.json',
        ('flask_argon', 'filter1', 0, 'top'),
        [
            ('flask_argon', 'valve_dry', (0, 1)),
            ('valve_dry', 'valve_filter', (5, 4)),
            ('valve_filter', 'filter1', (3, 'top')),
        ],
    ),
]

def test_pathfinding():
    """Test that correct paths are found on given graphs between given nodes."""
    for graph, target, path in tests:

        # Get target nodes to find path for
        src_port, dest_port = None, None
        through_nodes = []
        if len(target) == 5:
            src, dest, src_port, dest_port, through_nodes = target
        elif len(target) == 4:
            src, dest, src_port, dest_port = target
        elif len(target) == 2:
            src, dest

        # Instantiate Chempiler from graph
        c = Chempiler(experiment_code="test",
                      output_dir="out",
                      simulation=True,
                      graph_file=os.path.join(GRAPH_FOLDER, graph),
                      device_modules=[ChemputerAPI])

        # Path shouldn't be found for this target, make sure no false positive
        # path is found.
        if path is None:
            with pytest.raises(NetworkXNoPath):
                movement_path = c.graph.find_path(
                    src,
                    dest,
                    src_port,
                    dest_port,
                    through_nodes,
                    use_backbone=True
                )
                print('Found path', movement_path)

        # Path should be found for this target, check all steps in path are
        # correct and execute path simulation.
        else:
            movement_path = c.graph.find_path(
                src, dest, src_port, dest_port, through_nodes, use_backbone=True
            )
            print('Found path', movement_path)
            # Normal path
            if type(path[0]) != list:
                assert len(movement_path) == len(path)
                for i in range(len(movement_path)):
                    assert movement_path[i].as_tuple() == path[i]

            # Alternative path
            else:
                assert len(movement_path[0]) == len(path[0])
                assert len(movement_path[1]) == len(path[1])
                for i in range(len(movement_path[0])):
                    assert movement_path[0][i].as_tuple() == path[0][i]
                for i in range(len(movement_path[1])):
                    assert movement_path[1][i].as_tuple() == path[1][i]
            c.move(
                src=src,
                dest=dest,
                volume=10,
                src_port=src_port,
                dest_port=dest_port,
                through_nodes=through_nodes,
                use_backbone=True,
            )
