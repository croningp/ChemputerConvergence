import logging
import pytest
import os
import sys
import ChemputerAPI
from chempiler import Chempiler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.append(ROOT)
TEST_GRAPH = os.path.join(HERE, "graph_files", "bigrig.json")


ORGSYN_V83P0193_PIPELINE_TESTS = [
    (
        {'src': 'flask_water', 'dest': 'separator', 'volume': 10, 'speed': 40},
        [
            [
                ("valve_H", {'cmd': ('route', 3, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('sink', 0), 'volume': 10, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 1, -1)}),
                ("valve_G", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 10, 'speed': 40}),
                ("pump_G", {'cmd': ('sink', 0), 'volume': 10, 'speed': 40}),
            ],
            [
                ("valve_G", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_G", {'cmd': ('source', 0), 'volume': 10, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 10, 'speed': 40}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('source', 0), 'volume': 10, 'speed': 40}),
            ],
        ]
    ),

    (
        {'src': 'flask_water', 'dest': 'separator', 'volume': 40, 'speed': 40},
        [
            [
                ("valve_H", {'cmd': ('route', 3, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 1, -1)}),
                ("valve_G", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 3, -1)}),
                ("valve_G", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('sink', 0), 'volume': 15, 'speed': 40}),
                ("pump_G", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 1, -1)}),
                ("valve_G", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 15, 'speed': 40}),
                ("pump_G", {'cmd': ('sink', 0), 'volume': 15, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_G", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_G", {'cmd': ('source', 0), 'volume': 15, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 15, 'speed': 40}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('source', 0), 'volume': 15, 'speed': 40}),
            ],
        ]
    ),

    (
        {'src': 'flask_water', 'dest': 'separator', 'volume': 50, 'speed': 40},
        [
            [
                ("valve_H", {'cmd': ('route', 3, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 1, -1)}),
                ("valve_G", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 3, -1)}),
                ("valve_G", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 1, -1)}),
                ("valve_G", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_G", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_G", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
        ]
    ),

    (
        {'src': 'flask_water', 'dest': 'separator', 'volume': 100, 'speed': 40},
        [
            [
                ("valve_H", {'cmd': ('route', 3, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 1, -1)}),
                ("valve_G", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 3, -1)}),
                ("valve_G", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 1, -1)}),
                ("valve_G", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 3, -1)}),
                ("valve_G", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 1, -1)}),
                ("valve_G", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 3, -1)}),
                ("valve_G", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 1, -1)}),
                ("valve_G", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_G", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_G", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
        ]
    ),

    (
        {'src': 'flask_water', 'dest': 'reactor', 'volume': 50, 'speed': 40},
        [
            [
                ("valve_H", {'cmd': ('route', 3, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 3, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
        ]
    ),

    (
        {
            'src': 'phase_B',
            'dest': 'separator',
            'volume': 50,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        [
            [
                ("valve_Y", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 60}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 60}),
            ],
        ]
    ),

    (
        {
            'src': 'phase_B',
            'dest': 'reactor',
            'volume': 50,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        [
            [
                ("valve_Y", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 2, -1)}),
                ("valve_G", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 5, -1)}),
                ("valve_G", {'cmd': ('route', 2, -1)}),
                ("valve_H", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
                ("pump_G", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_H", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 2, -1)}),
                ("valve_G", {'cmd': ('route', 1, -1)}),
                ("valve_H", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_G", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_H", {'cmd': ('source', 0), 'volume': 25, 'speed': 60}),
            ],
            [
                ("valve_G", {'cmd': ('route', 2, -1)}),
                ("valve_H", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_G", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_H", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_H", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_H", {'cmd': ('source', 0), 'volume': 25, 'speed': 60}),
            ],
        ]
    ),

    (
        {
            'src': 'phase_B',
            'dest': 'pump_Y',
            'volume': 25,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        [
            [
                ("valve_Y", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
            ],
        ]
    ),

    # Move  to invalid port
    (
        {
            'src': 'reactor',
            'dest': 'separator',
            'volume': 50,
            'dest_port': 'top',
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        'err'
    ),

    # Volume greater than dest pump volume
    (
        {
            'src': 'phase_B',
            'dest': 'pump_Y',
            'volume': 50,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        'err'
    ),

    # Volume greater than src pump volume
    (
        {
            'src': 'pump_Y',
            'dest': 'phase_B',
            'volume': 50,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        'err'
    ),

    # Move to pump
    (
        {
            'src': 'phase_B',
            'dest': 'pump_Y',
            'volume': 25,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        [
            [
                ("valve_Y", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
            ],
        ]
    ),

    # Move from pump
    (
        {
            'src': 'pump_Y',
            'dest': 'phase_B',
            'volume': 25,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        [
            [
                ("valve_Y", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 60}),
            ],
        ]
    ),

    # Move from/to same node.
    (
        {
            'src': 'phase_B',
            'dest': 'phase_B',
            'volume': 50,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        'err'
    ),

    (
        {
            'src': 'flask_hexane',
            'dest': 'separator',
            'volume': 200,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 40
        },
        [
            [
                ("valve_X", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
            ],
            [
                ("valve_X", {'cmd': ('route', 2, -1)}),
                ("valve_K", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_K", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 1, -1)}),
                ("valve_K", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
                ("pump_K", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 2, -1)}),
                ("valve_K", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_K", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 1, -1)}),
                ("valve_K", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
                ("pump_K", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 2, -1)}),
                ("valve_K", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_K", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 1, -1)}),
                ("valve_K", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
                ("pump_K", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 2, -1)}),
                ("valve_K", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_K", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 1, -1)}),
                ("valve_K", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
                ("pump_K", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 2, -1)}),
                ("valve_K", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_K", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 1, -1)}),
                ("valve_K", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
                ("pump_K", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 2, -1)}),
                ("valve_K", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_K", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 1, -1)}),
                ("valve_K", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
                ("pump_K", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 2, -1)}),
                ("valve_K", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_K", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 1, -1)}),
                ("valve_K", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('sink', 0), 'volume': 25, 'speed': 10}),
                ("pump_K", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_X", {'cmd': ('route', 2, -1)}),
                ("valve_K", {'cmd': ('route', 1, -1)}),
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_K", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_K", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_K", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 25, 'speed': 40}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('source', 0), 'volume': 25, 'speed': 40}),
            ],
        ]
    ),

    # Make sure default ports assigned correctly. Rotavap -> waste should use
    # evaporate port if no port is specified.
    (
        {
            'src': 'rotavap',
            'dest': 'waste_Y',
            'volume': 10,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        [
            [
                ("valve_X", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('sink', 0), 'volume': 10, 'speed': 10}),
            ],
            [
                ("valve_X", {'cmd': ('route', 2, -1)}),
                ("valve_K", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_X", {'cmd': ('source', 0), 'volume': 10, 'speed': 40}),
                ("pump_K", {'cmd': ('sink', 0), 'volume': 10, 'speed': 40}),
            ],
            [
                ("valve_K", {'cmd': ('route', 2, -1)}),
                ("valve_Y", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_K", {'cmd': ('source', 0), 'volume': 10, 'speed': 40}),
                ("pump_Y", {'cmd': ('sink', 0), 'volume': 10, 'speed': 40}),
            ],
            [
                ("valve_Y", {'cmd': ('route', 0, -1)}),
            ],
            [
                ("pump_Y", {'cmd': ('source', 0), 'volume': 10, 'speed': 60}),
            ],
        ]
    ),
]

DISCOVERY_PIPELINE_TESTS = [
    # Move pump volume through two valves to node on same valve.
    (
        {
            'src': 'reactor_7',
            'dest': 'waste_7',
            'volume': 5,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        [
            [
                ("valve_5", {'cmd': ('route', 2, -1)}),
                ("valve_7", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_51", {'cmd': ('sink', 0), 'volume': 5, 'speed': 10}),
            ],
            [
                ("valve_5", {'cmd': ('route', 2, -1)}),
                ("valve_7", {'cmd': ('route', -1, 3)}),
            ],
            [
                ("pump_51", {'cmd': ('source', 0), 'volume': 5, 'speed': 60}),
            ],
        ]
    ),

    # Move greater than pump volume through two valves to node on same valve.
    (
        {
            'src': 'reactor_7',
            'dest': 'waste_7',
            'volume': 10,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        [
            [
                ("valve_5", {'cmd': ('route', 2, -1)}),
                ("valve_7", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_51", {'cmd': ('sink', 0), 'volume': 5, 'speed': 10}),
            ],
            [
                ("valve_5", {'cmd': ('route', 2, -1)}),
                ("valve_7", {'cmd': ('route', -1, 3)}),
            ],
            [
                ("pump_51", {'cmd': ('source', 0), 'volume': 5, 'speed': 60}),
            ],
            [
                ("valve_5", {'cmd': ('route', 2, -1)}),
                ("valve_7", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_51", {'cmd': ('sink', 0), 'volume': 5, 'speed': 10}),
            ],
            [
                ("valve_5", {'cmd': ('route', 2, -1)}),
                ("valve_7", {'cmd': ('route', -1, 3)}),
            ],
            [
                ("pump_51", {'cmd': ('source', 0), 'volume': 5, 'speed': 60}),
            ],
        ]
    ),

    # Move pump volume through two valves to node on different valve.
    (
        {
            'src': 'reactor_7',
            'dest': 'waste_6',
            'volume': 5,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        [
            [
                ("valve_5", {'cmd': ('route', 2, -1)}),
                ("valve_7", {'cmd': ('route', 1, -1)}),
                ("valve_3", {'cmd': ('route', -1, 3)}),
            ],
            [
                ("pump_51", {'cmd': ('sink', 0), 'volume': 5, 'speed': 10}),
            ],
            [
                ("valve_5", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_51", {'cmd': ('source', 0), 'volume': 5, 'speed': 60}),
            ],
        ]
    ),

    # Move greater than pump volume through two valves to node on same valve.
    (
        {
            'src': 'reactor_7',
            'dest': 'waste_6',
            'volume': 10,
            'initial_pump_speed': 10,
            'mid_pump_speed': 40,
            'end_pump_speed': 60
        },
        [
            [
                ("valve_5", {'cmd': ('route', 2, -1)}),
                ("valve_7", {'cmd': ('route', 1, -1)}),
                ("valve_3", {'cmd': ('route', -1, 3)}),
            ],
            [
                ("pump_51", {'cmd': ('sink', 0), 'volume': 5, 'speed': 10}),
            ],
            [
                ("valve_5", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_51", {'cmd': ('source', 0), 'volume': 5, 'speed': 60}),
            ],
            [
                ("valve_5", {'cmd': ('route', 2, -1)}),
            ],
            [
                ("pump_51", {'cmd': ('sink', 0), 'volume': 5, 'speed': 10}),
            ],
            [
                ("valve_5", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_51", {'cmd': ('source', 0), 'volume': 5, 'speed': 60}),
            ],
        ]
    ),
]

DMP_TEST_GRAPH_TESTS = [
    (
        {
            'src': "flask_oxone_aq",
            'dest': "rotavap",
            'volume': 15,
            'initial_pump_speed': 10,
            'mid_pump_speed': 10,
            'end_pump_speed': 10,
            'through_nodes': ["flask_separator", "cartridge_drying"]
        },
        [
            [
                ("valve_filter", {'cmd': ('route', 1, -1)}),
            ],
            [
                (
                    "pump_filter",
                    {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_filter", {'cmd': ('route', 4, -1)}),
                ("valve_dry", {'cmd': ('route', 5, -1)}),
            ],
            [
                (
                    "pump_filter",
                    {'cmd': ('source', 0), 'volume': 15, 'speed': 10}
                ),
                ("pump_dry", {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}),
            ],
            [
                ("valve_dry", {'cmd': ('route', 4, -1)}),
                ("valve_organic", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_dry", {'cmd': ('source', 0), 'volume': 15, 'speed': 10}),
                ("pump_air", {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}),
            ],
            [
                ("valve_organic", {'cmd': ('route', 4, -1)}),
                ("valve_separator", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_air", {'cmd': ('source', 0), 'volume': 15, 'speed': 10}),
                (
                    "pump_workup",
                    {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_separator", {'cmd': ('route', 3, -1)}),
            ],
            [
                (
                    "pump_workup",
                    {'cmd': ('source', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_separator", {'cmd': ('route', 3, -1)}),
            ],
            [
                (
                    "pump_workup",
                    {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_separator", {'cmd': ('route', 1, -1)}),
                ("valve_rotavap", {'cmd': ('route', 1, -1)}),
            ],
            [
                (
                    "pump_workup",
                    {'cmd': ('source', 0), 'volume': 15, 'speed': 10}
                ),
                (
                    "pump_rotavap",
                    {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_rotavap", {'cmd': ('route', 3, -1)}),
            ],
            [
                (
                    "pump_rotavap",
                    {'cmd': ('source', 0), 'volume': 15, 'speed': 10}
                ),
            ],
        ]
    ),

    (
        {
            'src': "flask_oxone_aq",
            'dest': "rotavap",
            'volume': 15,
            'initial_pump_speed': 10,
            'mid_pump_speed': 10,
            'end_pump_speed': 10,
            'through_nodes': ["cartridge_drying"]
        },
        [
            [
                ("valve_filter", {'cmd': ('route', 1, -1)}),
            ],
            [
                (
                    "pump_filter",
                    {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_filter", {'cmd': ('route', 4, -1)}),
                ("valve_dry", {'cmd': ('route', 5, -1)}),
            ],
            [
                (
                    "pump_filter",
                    {'cmd': ('source', 0), 'volume': 15, 'speed': 10}
                ),
                ("pump_dry", {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}),
            ],
            [
                ("valve_dry", {'cmd': ('route', 4, -1)}),
                ("valve_organic", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_dry", {'cmd': ('source', 0), 'volume': 15, 'speed': 10}),
                ("pump_air", {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}),
            ],
            [
                ("valve_organic", {'cmd': ('route', 4, -1)}),
                ("valve_separator", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_air", {'cmd': ('source', 0), 'volume': 15, 'speed': 10}),
                (
                    "pump_workup",
                    {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_separator", {'cmd': ('route', 1, -1)}),
                ("valve_rotavap", {'cmd': ('route', 1, -1)}),
            ],
            [
                (
                    "pump_workup",
                    {'cmd': ('source', 0), 'volume': 15, 'speed': 10}
                ),
                (
                    "pump_rotavap",
                    {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_rotavap", {'cmd': ('route', 3, -1)}),
            ],
            [
                (
                    "pump_rotavap",
                    {'cmd': ('source', 0), 'volume': 15, 'speed': 10}
                ),
            ],
        ]
    ),

    (
        {
            'src': "flask_oxone_aq",
            'dest': "rotavap",
            'volume': 15,
            'initial_pump_speed': 10,
            'mid_pump_speed': 10,
            'end_pump_speed': 10,
            'through_nodes': ["flask_separator"]
        },
        [
            [
                ("valve_filter", {'cmd': ('route', 1, -1)}),
            ],
            [
                (
                    "pump_filter",
                    {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_filter", {'cmd': ('route', 4, -1)}),
                ("valve_dry", {'cmd': ('route', 5, -1)}),
            ],
            [
                (
                    "pump_filter",
                    {'cmd': ('source', 0), 'volume': 15, 'speed': 10}
                ),
                ("pump_dry", {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}),
            ],
            [
                ("valve_dry", {'cmd': ('route', 4, -1)}),
                ("valve_organic", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_dry", {'cmd': ('source', 0), 'volume': 15, 'speed': 10}),
                ("pump_air", {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}),
            ],
            [
                ("valve_organic", {'cmd': ('route', 4, -1)}),
                ("valve_separator", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_air", {'cmd': ('source', 0), 'volume': 15, 'speed': 10}),
                (
                    "pump_workup",
                    {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_separator", {'cmd': ('route', 3, -1)}),
            ],
            [
                (
                    "pump_workup",
                    {'cmd': ('source', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_separator", {'cmd': ('route', 3, -1)}),
            ],
            [
                (
                    "pump_workup",
                    {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_separator", {'cmd': ('route', 4, -1)}),
                ("valve_rotavap", {'cmd': ('route', 5, -1)}),
            ],
            [
                (
                    "pump_workup",
                    {'cmd': ('source', 0), 'volume': 15, 'speed': 10}
                ),
                (
                    "pump_rotavap",
                    {'cmd': ('sink', 0), 'volume': 15, 'speed': 10}
                ),
            ],
            [
                ("valve_rotavap", {'cmd': ('route', 3, -1)}),
            ],
            [
                (
                    "pump_rotavap",
                    {'cmd': ('source', 0), 'volume': 15, 'speed': 10}
                ),
            ],
        ]
    ),
]

ALKYL_FLUOR_GRAPH_TESTS = [
    (
        {
            'src': 'rotavap',
            'dest': 'buffer_flask',
            'src_port': 'evaporate',
            'dest_port': '0',
            'volume': 40,
            'initial_pump_speed': 20,
            'mid_pump_speed': 30,
            'end_pump_speed': 40,
            'through_nodes': 'cartridge_celite_C'
        },
        [
            [
                ("valve_F", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_F", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 20}),
            ],
            [
                ("valve_F", {'cmd': ('route', 2, -1)}),
                ("valve_E", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_F", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 30}),
                ("pump_E", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 30}),
            ],
            [
                ("valve_E", {'cmd': ('route', 2, -1)}),
                ("valve_D", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_E", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 30}),
                ("pump_D", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 30}),
            ],
            [
                ("valve_D", {'cmd': ('route', 5, -1)}),
                ("valve_E", {'cmd': ('route', 3, -1)}),
            ],
            [
                ("pump_D", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 20}),
                ("pump_E", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 20}),
            ],
            [
                ("valve_E", {'cmd': ('route', 2, -1)}),
                ("valve_D", {'cmd': ('route', 1, -1)}),
                ("valve_F", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_E", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 30}),
                ("pump_D", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 30}),
                ("pump_F", {'cmd': ('sink', 0), 'volume': 15.0, 'speed': 20}),
            ],
            [
                ("valve_D", {'cmd': ('route', 2, -1)}),
                ("valve_C", {'cmd': ('route', 1, -1)}),
                ("valve_F", {'cmd': ('route', 2, -1)}),
                ("valve_E", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_D", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 30}),
                ("pump_C", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 30}),
                ("pump_F", {'cmd': ('source', 0), 'volume': 15.0, 'speed': 30}),
                ("pump_E", {'cmd': ('sink', 0), 'volume': 15.0, 'speed': 30}),
            ],
            [
                ("valve_C", {'cmd': ('route', 5, -1)}),
                ("valve_E", {'cmd': ('route', 2, -1)}),
                ("valve_D", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_C", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 40}),
                ("pump_E", {'cmd': ('source', 0), 'volume': 15.0, 'speed': 30}),
                ("pump_D", {'cmd': ('sink', 0), 'volume': 15.0, 'speed': 30}),
            ],
            [
                ("valve_D", {'cmd': ('route', 5, -1)}),
                ("valve_E", {'cmd': ('route', 3, -1)}),
            ],
            [
                ("pump_D", {'cmd': ('source', 0), 'volume': 15.0, 'speed': 20}),
                ("pump_E", {'cmd': ('sink', 0), 'volume': 15.0, 'speed': 20}),
            ],
            [
                ("valve_E", {'cmd': ('route', 2, -1)}),
                ("valve_D", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_E", {'cmd': ('source', 0), 'volume': 15.0, 'speed': 30}),
                ("pump_D", {'cmd': ('sink', 0), 'volume': 15.0, 'speed': 30}),
            ],
            [
                ("valve_D", {'cmd': ('route', 2, -1)}),
                ("valve_C", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_D", {'cmd': ('source', 0), 'volume': 15.0, 'speed': 30}),
                ("pump_C", {'cmd': ('sink', 0), 'volume': 15.0, 'speed': 30}),
            ],
            [
                ("valve_C", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_C", {'cmd': ('source', 0), 'volume': 15.0, 'speed': 40}),
            ],
        ]
    ),
]

AF_RBF_TESTS = [
    (
        {
            'src': 'rotavap',
            'dest': 'buffer_flask',
            'volume': 2.0,
            'src_port': 'evaporate',
            'dest_port': 0,
            'speed': None,
            'initial_pump_speed': 5,
            'mid_pump_speed': 5,
            'end_pump_speed': 40,
            'through_nodes': ['cartridge_celite'],
            'use_backbone': True
        },
        [
            [
                ("valve_E", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_E", {'cmd': ('sink', 0), 'volume': 2.0, 'speed': 5}),
            ],
            [
                ("valve_E", {'cmd': ('route', 2, -1)}),
                ("valve_C", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_E", {'cmd': ('source', 0), 'volume': 2.0, 'speed': 5}),
                ("pump_C", {'cmd': ('sink', 0), 'volume': 2.0, 'speed': 5}),
            ],
            [
                ("valve_C", {'cmd': ('route', 5, -1)}),
                ("valve_E", {'cmd': ('route', 3, -1)}),
            ],
            [
                ("pump_C", {'cmd': ('source', 0), 'volume': 2.0, 'speed': 5}),
                ("pump_E", {'cmd': ('sink', 0), 'volume': 2.0, 'speed': 5}),
            ],
            [
                ("valve_E", {'cmd': ('route', 2, -1)}),
                ("valve_C", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_E", {'cmd': ('source', 0), 'volume': 2.0, 'speed': 5}),
                ("pump_C", {'cmd': ('sink', 0), 'volume': 2.0, 'speed': 5}),
            ],
            [
                ("valve_C", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_C", {'cmd': ('source', 0), 'volume': 2.0, 'speed': 40}),
            ],
        ]
    ),
    (
        {
            'src': 'rotavap',
            'dest': 'buffer_flask',
            'volume': 50.0,
            'src_port': 'evaporate',
            'dest_port': 0,
            'speed': None,
            'initial_pump_speed': 5,
            'mid_pump_speed': 5,
            'end_pump_speed': 40,
            'through_nodes': ['cartridge_celite'],
            'use_backbone': True
        },
        [
            [
                ("valve_E", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_E", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 5}),
            ],
            [
                ("valve_E", {'cmd': ('route', 2, -1)}),
                ("valve_C", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_E", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 5}),
                ("pump_C", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 5}),
            ],
            [
                ("valve_C", {'cmd': ('route', 5, -1)}),
                ("valve_E", {'cmd': ('route', 3, -1)}),
            ],
            [
                ("pump_C", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 5}),
                ("pump_E", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 5}),
            ],
            [
                ("valve_E", {'cmd': ('route', 2, -1)}),
                ("valve_C", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_E", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 5}),
                ("pump_C", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 5}),
            ],
            [
                ("valve_C", {'cmd': ('route', 4, -1)}),
                ("valve_E", {'cmd': ('route', 5, -1)}),
            ],
            [
                ("pump_C", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 40}),
                ("pump_E", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 5}),
            ],
            [
                ("valve_E", {'cmd': ('route', 2, -1)}),
                ("valve_C", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_E", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 5}),
                ("pump_C", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 5}),
            ],
            [
                ("valve_C", {'cmd': ('route', 5, -1)}),
                ("valve_E", {'cmd': ('route', 3, -1)}),
            ],
            [
                ("pump_C", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 5}),
                ("pump_E", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 5}),
            ],
            [
                ("valve_E", {'cmd': ('route', 2, -1)}),
                ("valve_C", {'cmd': ('route', 1, -1)}),
            ],
            [
                ("pump_E", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 5}),
                ("pump_C", {'cmd': ('sink', 0), 'volume': 25.0, 'speed': 5}),
            ],
            [
                ("valve_C", {'cmd': ('route', 4, -1)}),
            ],
            [
                ("pump_C", {'cmd': ('source', 0), 'volume': 25.0, 'speed': 40}),
            ],
        ]
    ),
]

def test_pipelining_detailed():
    for graph, correct_pipelines in [
        ('orgsyn_v83p0193_graph.json', ORGSYN_V83P0193_PIPELINE_TESTS),
        ('discovery_graph.json', DISCOVERY_PIPELINE_TESTS),
        ('DMP_graph_test.json', DMP_TEST_GRAPH_TESTS),
        ('AlkylFluor_full.graphml', ALKYL_FLUOR_GRAPH_TESTS),
        ('AF-4-Tr-RBF.graphml', AF_RBF_TESTS),
    ]:
        test_pipelines(graph, correct_pipelines)

def test_pipelines(graph, correct_pipelines):
    test_graph = os.path.join(HERE, 'graph_files', graph)
    c = Chempiler(
        experiment_code="test_suite",
        graph_file=test_graph,
        output_dir=".",
        simulation=True,
        device_modules=[ChemputerAPI]
    )

    logger = logging.getLogger('chempiler')
    logger.setLevel(logging.DEBUG)

    for move_params, correct_pipelined_steps in correct_pipelines:
        logger.debug(graph, move_params)
        if correct_pipelined_steps == 'err':
            with pytest.raises(Exception):
                c.move(**move_params)
        else:
            pipelined_steps = c.move(**move_params)
            try:
                assert len(pipelined_steps) == len(correct_pipelined_steps)
                for i, step_group in enumerate(pipelined_steps):
                    correct_step_group = correct_pipelined_steps[i]
                    assert len(step_group) == len(correct_step_group)
                    for j, step in enumerate(step_group):
                        correct_step = correct_step_group[j]
                        assert step[0].name == correct_step[0]
                        assert step[1]['cmd'] == correct_step[1]['cmd']
                        for item in ['volume', 'speed']:
                            if item in correct_step[1]:
                                assert item in step[1]
                                assert step[1][item] == correct_step[1][item]
            except AssertionError as e:
                for step_group in pipelined_steps:
                    for step in step_group:
                        print(step[0].name, step[1])
                    print('\n')
                print('Failed on', move_params)
                raise e
