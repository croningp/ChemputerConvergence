"""
(c) 2019 The Cronin Group, University of Glasgow

This file contains all constants used in the Chempiler project,
such as dictionary keys, device types, and so forth. Keeping them
all in one file makes future maintenance a lot easier and avoids duplicates.
"""
from typing import Dict, List

DEFAULT_INITIAL_PUMP_SPEED = 40
DEFAULT_END_PUMP_SPEED = 40
DEFAULT_MID_PUMP_SPEED = 40

# numerical constants (in alphabetical order)
ATMOSPHERIC_PRESSURE = 900
COOLING_THRESHOLD = 0.5  # degrees
SEPARATION_DEAD_VOLUME = 2.5
SEPARATION_DEFAULT_INITIAL_PUMP_SPEED = 10  # mL/min
SEPARATION_DEFAULT_MID_PUMP_SPEED = 40  # mL/min
SEPARATION_DEFAULT_END_PUMP_SPEED = 40  # mL/min
SEPARATION_DEFAULT_PRIMING_VOLUME = 2  # mL

# Assumption of Chempiler. Port that pump will be connected to valve.
PUMP_PORT: int = -1

VALID_PORTS: Dict[str, List[str]] = {
    'ChemputerSeparator': ['top', 'bottom'],
    'ChemputerReactor': ['0', '1', '2'],
    'ChemputerFilter': ['top', 'bottom'],
    'ChemputerPump': ['0'],
    'IKARV10': ['evaporate', 'collect'],
    'ChemputerValve': ['-1', '0', '1', '2', '3', '4', '5'],
    'ChemputerFlask': ['0'],
    'ChemputerWaste': ['0'],
    'ChemputerCartridge': ['0'],
}

DEFAULT_PORTS: Dict[str, Dict[str, str]] = {
    'ChemputerSeparator': {'src': 'bottom', 'dest': 'bottom'},
    'ChemputerReactor': {'src': 0, 'dest': 0},
    'ChemputerFilter': {'src': 'bottom', 'dest': 'top'},
    'ChemputerPump': {'src': 0, 'dest': 0},
    'IKARV10': {'src': 'evaporate', 'dest': 'evaporate'},
    'ChemputerFlask': {'src': 0, 'dest': 0},
    'ChemputerWaste': {'src': 0, 'dest': 0},
}

DEFAULT_CONNECT_PORTS: Dict[str, Dict[str, str]] = {
    'ChemputerSeparator': {'src': 'bottom', 'dest': 'bottom'},
    'ChemputerReactor': {'src': 0, 'dest': 0},
    'ChemputerFilter': {'src': 'bottom', 'dest': 'bottom'},
    'ChemputerPump': {'src': 0, 'dest': 0},
    'IKARV10': {'src': 'evaporate', 'dest': 'evaporate'},
    'ChemputerFlask': {'src': 0, 'dest': 0},
    'ChemputerWaste': {'src': 0, 'dest': 0},
}
