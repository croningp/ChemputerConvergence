import ChemputerAPI
from chempiler import Chempiler
import os

HERE = os.path.abspath(os.path.dirname(__file__))

TEST_GRAPH = os.path.join(HERE, "graph_files", "bigrig.json")

def test_separate_phases():
    c = Chempiler(
        experiment_code="test_suite",
        graph_file=TEST_GRAPH,
        output_dir=".",
        simulation=True,
        device_modules=[ChemputerAPI]
    )
    c.pump.separate_phases(
        lower_phase_target='waste_separator',
        dead_volume_target='waste_separator',
        upper_phase_target='waste_filter',
        separator_flask='separator'
    )
