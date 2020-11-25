import logging
import pytest
import os
import sys
import ChemputerAPI
from chempiler import Chempiler
from chempiler.tools.errors import IllegalPortError

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

logging.getLogger('chempiler').setLevel(logging.DEBUG)

def test_move_low_volume():
    # Move liquid at max volume
    c.move(
        "flask_oxone_aq",
        "rotavap",
        volume=25,
        initial_pump_speed=20,
        mid_pump_speed=20,
        end_pump_speed=20,
        through_nodes="cartridge_drying"
    )

    # Move liquid below max volume
    c.move(
        "flask_oxone_aq",
        "rotavap",
        volume=10,
        initial_pump_speed=20,
        mid_pump_speed=15,
        end_pump_speed=10,
        through_nodes="cartridge_drying"
    )

def test_move_high_volume():
    # Move liquid above max_volume
    c.move(
        "flask_oxone_aq",
        "rotavap",
        volume=40,
        initial_pump_speed=10,
        mid_pump_speed=10,
        end_pump_speed=10,
        through_nodes="cartridge_drying"
    )

    # Move liquid just above max volume
    c.move(
        "flask_oxone_aq",
        "rotavap",
        volume=26,
        initial_pump_speed=10,
        mid_pump_speed=10,
        end_pump_speed=10,
        through_nodes="cartridge_drying"
    )

    # Move liquid with ridiculous volume
    c.move(
        "flask_oxone_aq",
        "rotavap",
        volume=986,
        initial_pump_speed=10,
        mid_pump_speed=20,
        end_pump_speed=20,
        through_nodes="cartridge_drying"
    )

def test_move_fractional_volume():
    # Move partial volume
    c.move(
        "flask_oxone_aq",
        "rotavap",
        volume=27.3,
        initial_pump_speed=22,
        mid_pump_speed=17,
        end_pump_speed=12,
        through_nodes="cartridge_drying"
    )

def test_move_multiple_through_nodes():
    # Move through two nodes, one with the same pump as the src and dest
    c.move(
        "flask_oxone_aq",
        "rotavap",
        volume=15,
        initial_pump_speed=10,
        mid_pump_speed=10,
        end_pump_speed=10,
        through_nodes=["flask_separator", "cartridge_drying"]
    )

def test_phase_separation():
    c.pump.separate_phases(
        "flask_separator",
        lower_phase_target="waste_workup",
        upper_phase_target="flask_separator"
    )

def test_illegal_port_catching():
    c.move(
        "flask_oxone_aq", "rotavap", volume=15, speed=40, dest_port="evaporate")
    c.move("flask_oxone_aq", "filter1", volume=15, speed=40, dest_port="top")
    c.move("flask_oxone_aq", "filter1", volume=15, speed=40, dest_port="bottom")

    with pytest.raises(IllegalPortError):
        c.move(
            "flask_oxone_aq", "rotavap", volume=15, speed=40, dest_port="top")
        c.move(
            "flask_oxone_aq",
            "filter1",
            volume=15,
            speed=40,
            dest_port="evaporate"
        )
