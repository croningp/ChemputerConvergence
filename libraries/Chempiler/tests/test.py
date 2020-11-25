import ChemputerAPI
from chempiler import Chempiler
import os
import logging

HERE = os.path.abspath(os.path.dirname(__file__))

DISCOVERY_GRAPH = 'tests/graph_files/discovery_graph.json'
ORGSYN_V83P0193_GRAPH =\
    'tests/graph_files/orgsyn_v83p0193_graph.json'
ORGSYN_V83p0184A_GRAPH =\
    '/home/group/XDL/tests/integration/files/orgsyn_v83p0184a_graph.json'

DESKTOP = '/home/group/Desktop/'
ALKYL_FLUOR_GRAPH =\
    '/home/group/XDL/tests/integration/files/AlkylFluor_graph.graphml'
AF_RBF_GRAPH = '/home/group/XDL/tests/unit/files/AF-4-Tr-RBF.graphml'
DMP_GRAPH = '/home/group/Chempiler/tests/graph_files/DMP_graph_test.json'
GRAPH = '/home/group/XDL/tests/integration/files/AlkylFluor_graph.graphml'
DK_GRAPH = '/home/group/Desktop/ALChem_v8_var1.json'


c = Chempiler(
    experiment_code="test",
    graph_file=AF_RBF_GRAPH,
    output_dir="/home/group/Desktop",
    simulation=True,
    device_modules=[ChemputerAPI]
)
logging.getLogger('chempiler').setLevel(logging.DEBUG)

c.move(
    **{
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
    }
)
# c.move(
#     **{
#         'src': 'flask_oxone_aq',
#         'dest': 'rotavap',
#         'volume': 15,
#         'initial_pump_speed': 10,
#         'mid_pump_speed': 10,
#         'end_pump_speed': 10,
#         'through_nodes': ['flask_separator', 'cartridge_drying']
#     }
# )


# from xdl import XDL
# x = XDL(os.path.join(DESKTOP, 'orgsyn_v90p0251_para1.xdl'))
# x.prepare_for_execution(GRAPH)
# x.execute(c)

# c.move(
#     'rotavap',
#     'waste_Y',
#     volume=10,
#     initial_pump_speed=10,
#     mid_pump_speed=40,
#     end_pump_speed=60
# )
