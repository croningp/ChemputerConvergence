# coding=utf-8
# !/usr/bin/env python
"""
"shaker_stirrer" -- API for Cronin shaker stirrer device
===================================

.. module:: shaker_stirrer
   :platform: Windows
   :synopsis: Read the Cronin conductivity sensor.
   :license: BSD 3-clause
.. moduleauthor:: S. Hessam M. Mehr <Hessam.Mehr@glasgow.ac.uk>
.. moduleauthor:: Davide Angelone <Davide.Angelone@glasgow.ac.uk>

(c) 2018 The Cronin Group, University of Glasgow

This is a simple device for shaking/stirring small vials.
"""

# system imports
import re
import serial
from time import sleep

# additional module imports
from SerialLabware.serial_labware import SerialDevice, command


class ShakerStirrer(SerialDevice):
    """
    This provides a python class for the Cronin conductivity
    sensor.
    """

    def __init__(self, port=None, device_name=None, milliseconds_on=500, milliseconds_off=2000, connect_on_instantiation=True,  soft_fail_for_testing=False, address=None, mode=None):
        """
        Initializer of the ShakerStirrer class

        Args:
            port (str): The port name/number of the pump
            device_name (str): A descriptive name for the device, used mainly in debug prints
            milliseconds_on (int or str): The number of milliseconds when the motor is running during each cycle
            milliseconds_off (int or str): The number of milliseconds when the motor is turned off during each cycle
        """

        # device properties
        self._on_ms = milliseconds_on
        self._off_ms = milliseconds_off

        # serial settings
        self.baudrate = 9600
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.rtscts = False
        self.timeout = 5

        # answer patterns
        self.getanswer = re.compile("([01]) ([0-9]+) ([0-9]+)\r\n")

        # DOCUMENTED COMMANDS for easier maintenance
        # general commands

        # shaker-stirrer commands
        self.START_STIRRER = "START"
        self.STOP_STIRRER = "STOP 0 0"

        super().__init__(address, port, mode, device_name, connect_on_instantiation, soft_fail_for_testing)


    def open_connection(self):
        super().open_connection()
        # Temporary delay for the device to settle down before the receiving the next command
        sleep(1)

    @command
    def start_stirrer(self):
        """
        Start the stirrer
        """
        self.logger.info(f"{self.__class__.__name__} {self.device_name} - Starting shaker-stirrer.")
        message = f"{self.START_STIRRER} {self._on_ms} {self._off_ms}"
        value = self.send_message(message, True, self.getanswer, multiline=False)
        return value

    @command
    def stop_stirrer(self):
        """
        Stops the stirrer
        """
        self.logger.info(f"{self.__class__.__name__} {self.device_name} - Stopping shaker-stirrer.")
        value = self.send_message(self.STOP_STIRRER, True, self.getanswer, multiline=False)
        return value

    @property
    def milliseconds_on(self):
        return self._on_ms

    @milliseconds_on.setter
    def milliseconds_on(self, on_ms):
        self.logger.info(f"{self.__class__.__name__} {self.device_name} - On milliseconds set to {on_ms}.")
        self._on_ms = on_ms
        self.stop_stirrer()
        self.start_stirrer()

    @property
    def milliseconds_off(self):
        return self._off_ms

    @milliseconds_off.setter
    def milliseconds_off(self, off_ms):
        self.logger.info(f"{self.__class__.__name__} {self.device_name} - Off milliseconds set to {off_ms}.")
        self._off_ms = off_ms
        self.stop_stirrer()
        self.start_stirrer()


if __name__ == '__main__':
    s = ShakerStirrer(port="COM4")
    print("Starting stirrer")
    print(s.start_stirrer())
    sleep(2)
    print("Changing duty cycle")
    s.milliseconds_on = 200
    s.milliseconds_off = 1000
    sleep(2)
    print("Stopping stirrer")
    print(s.stop_stirrer())
    print("Done")
