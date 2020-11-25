import os
import sys
import ChemputerAPI
from chempiler import Chempiler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.append(ROOT)
TEST_GRAPH = os.path.join(HERE, "graph_files", "DMP_graph_test.json")

c = Chempiler(
    experiment_code="test_suite",
    graph_file=TEST_GRAPH,
    output_dir=".",
    simulation=True,
    device_modules=[ChemputerAPI]
)

stirrer = c.stirrer
vacuum = c.vacuum
chiller = c.chiller

def test_stirrers():
    stirrer.stir("filter1")
    stirrer.stir("flask_separator")

    stirrer.set_stir_rate("filter1", 4000)
    stirrer.set_stir_rate("flask_separator", 10000)

    stirrer.stop_stir("filter1")
    stirrer.stop_stir("flask_separator")


def test_rotavap_and_vacuum():
    vacuum.initialise("rotavap")
    vacuum.get_vacuum_set_point("rotavap")
    vacuum.set_vacuum_set_point("rotavap", 100)
    vacuum.start_vacuum("rotavap")
    vacuum.stop_vacuum("rotavap")
    vacuum.vent_vacuum("rotavap")
    vacuum.get_status("rotavap")
    vacuum.get_end_vacuum_set_point("rotavap")
    vacuum.set_end_vacuum_set_point("rotavap", 100)
    vacuum.get_runtime_set_point("rotavap")
    vacuum.set_runtime_set_point("rotavap", 100)
    vacuum.set_speed_set_point("rotavap", 100)
    vacuum.auto_evaporation("rotavap")


def test_chiller():
    cf = "filter1"
    chiller.start_chiller(cf)
    chiller.set_temp(cf, -20)
    chiller.cooling_power(cf, 78)
    chiller.wait_for_temp(cf)
    chiller.stop_chiller(cf)
