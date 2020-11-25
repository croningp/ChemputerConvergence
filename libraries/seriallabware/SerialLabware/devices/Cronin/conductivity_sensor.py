# coding=utf-8
# !/usr/bin/env python
"""
"conductivity_sensor" -- API for Cronin conductivity sensor
===================================

.. module:: conductivity_sensor
   :platform: Windows
   :synopsis: Read the Cronin conductivity sensor.
   :license: BSD 3-clause
.. moduleauthor:: S. Hessam M. Mehr <Hessam.Mehr@glasgow.ac.uk>

(c) 2018 The Cronin Group, University of Glasgow

The current Cronin conductivity sensor measures solution conductivity against
a pair of resistors. The measured conductivities can then be reported back as
a tuple of 10-bit integers by sending the string `C` to the sensor. Alternatively, the
sensor can add up any measured conductivities and report them back as a single large
integer if the string `Q` is sent. This is useful for backwards compatibility as well
as the fact that a large change in conductivity against any single resistance is
typically indicative of a phase change.
"""

# system imports
import re
import serial
from time import sleep

# additional module imports
from SerialLabware.serial_labware import SerialDevice, command


class ConductivitySensor(SerialDevice):
    """
    This provides a python class for the Cronin conductivity
    sensor.
    """

    def __init__(self, port=None, device_name=None, connect_on_instantiation=True, soft_fail_for_testing=False, address=None, mode=None):
        """
        Initializer of the ConductivitySensor class

        Args:
            port (str): The port name/number of the pump
            device_name (str): A descriptive name for the device, used mainly in debug prints
            soft_fail_for_testing (bool): (optional) determines if an invalid serial port raises an error or merely logs
                a message. Default: False
        """
        # serial settings
        self.baudrate = 9600
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.rtscts = False

        # answer patterns
        self.getanswer = re.compile("([0-9]+)\r\n")
        self.getanswer_multiple = re.compile("([0-9 ]+)+\r\n")

        # DOCUMENTED COMMANDS for easier maintenance
        # general commands

        # conductivity sensor commands
        # read commands
        self.GET_CONDUCTIVITY = "Q"
        self.GET_CONDUCTIVITY_MULTIPLE = "C"
        # write commands

        super().__init__(address, port, mode, device_name, connect_on_instantiation, soft_fail_for_testing)


        if connect_on_instantiation:
            self.open_connection()

    def open_connection(self):
        super().open_connection()
        # Temporary delay for the device to settle down before the receiving the next command
        sleep(1)

    @property
    @command
    def conductivity(self):
        """
        Reads the current conductivity.

        Returns:
            An integer in the 0-1023 range
        """
        value = self.send_message(self.GET_CONDUCTIVITY, True, self.getanswer, multiline=False)
        return int(value[0])

    @property
    @command
    def conductivity_multiple(self):
        """
        Reads the current conductivity versus multiple resistances.

        Returns:
            A tuple of integers each in the 0-1023 range
        """
        value = self.send_message(self.GET_CONDUCTIVITY_MULTIPLE, True, self.getanswer_multiple, multiline=False)
        return tuple([int(reading) for reading in value[0].split()])

if __name__ == '__main__':
    p = ConductivitySensor(port="COM8")
    p.open_connection()
    print(p.conductivity)
    print(p.conductivity_multiple)
