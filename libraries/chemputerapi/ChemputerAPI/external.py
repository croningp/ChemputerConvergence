"""
Device classes from other packages. Re-exporting them here allows
capabilities to be overridden and means SerialLabware can be accessed through
ChemputerAPI.
"""

from typing import List, Tuple

import SerialLabware
from SerialLabware import *
from .flasks import ChemputerFlask

# Remove some device classes from namespaces
# so they can be overloaded.
for device_class_name in ['IKARV10', 'SimIKARV10']:
    del(globals()[device_class_name])

# IKA RV10 Rotavap
ikarv10_capabilities = [
    ('source', 'evaporate'), ('sink', 'evaporate'), ('source', 'collect')]

class IKARV10(SerialLabware.IKARV10, ChemputerFlask):
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def __init__(self, port=None, device_name=None, *args, **kwargs):
        SerialLabware.IKARV10.__init__(self, port, device_name)
        ChemputerFlask.__init__(self, *args, **kwargs)

    @property
    def capabilities(self):
        return ikarv10_capabilities


class SimIKARV10(SerialLabware.SimIKARV10, ChemputerFlask):
    def __init__(self, port=None, device_name=None, *args, **kwargs):
        SerialLabware.SimIKARV10.__init__(self, port, device_name)
        ChemputerFlask.__init__(self, *args, **kwargs)

    @property
    def capabilities(self):
        return ikarv10_capabilities
