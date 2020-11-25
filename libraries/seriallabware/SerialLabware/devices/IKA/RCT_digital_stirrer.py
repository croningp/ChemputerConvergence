# coding=utf-8
# !/usr/bin/env python
"""
"RCT_digital" -- API for IKA RCT digital remote controllable hotplate stirrer
===========================================================================================

.. module:: RCT_digital
   :platform: Windows
   :synopsis: Control IKA RCT digital hotplate stirrer.
   :license: BSD 3-clause
.. moduleauthor:: Cronin Group 2018

(c) 2018 The Cronin Group, University of Glasgow

This provides a Python class for the IKA RCT digital Hotplates.
The code is adapted from RET_Control_Visc_stirrer.py with additions/omissions based on the RCT digital manual (pages 103–104,
English version).

For style guide used see http://xkcd.com/1513/
"""

# system imports
import re
import serial

# Core import
from SerialLabware.serial_labware import SerialDevice, command


class IKARCTDigital(SerialDevice):
    """
    This provides a python class for the IKA RCT digital Hotplates.
    """

    def __init__(self, port=None, device_name=None, connect_on_instantiation=True, soft_fail_for_testing=False, address=None, mode=None):
        """
        Initializer of the IKARCTDigital class.

        Args:
            port (str): The port name/number of the hotplate
            device_name (str): A descriptive name for the device, used mainly in debug prints.
            connect_on_instantiation (bool): (optional) determines if the connection is established on instantiation of
                the class. Default: On
            soft_fail_for_testing (bool): (optional) determines if an invalid serial port raises an error or merely logs
                a message. Default: Off
        """

        # serial settings
        self.baudrate = 9600
        self.bytesize = serial.SEVENBITS
        self.parity = serial.PARITY_EVEN
        self.rtscts = True

        self.write_delay = 0.1
        self.read_delay = 0.1

        # answer patterns
        self.stranswer = re.compile("([0-9A-Z_]+)\r\n")
        self.valueanswer = re.compile("(\d+\.\d+) (\d)\r\n")
        self.wdanswer = re.compile("(\d+\.\d+)\r\n")

        # other settings
        self.IKA_default_name = "IKARCT"

        # DOCUMENTED COMMANDS for easier maintenance
        self.GET_STIR_RATE_PV = "IN_PV_4"
        self.GET_STIR_RATE_SP = "IN_SP_4"
        self.SET_STIR_RATE_SP = "OUT_SP_4"
        self.GET_TEMP_PV = "IN_PV_1"
        self.GET_TEMP_SP = "IN_SP_1"
        self.SET_TEMP_SP = "OUT_SP_1"
        self.START_TEMP = "START_1"
        self.STOP_TEMP = "STOP_1"
        self.START_STIR = "START_4"
        self.STOP_STIR = "STOP_4"
        self.RESET = "RESET"
        self.GET_NAME = "IN_NAME"
        self.GET_HOT_PLATE_TEMPERATURE_PV = "IN_PV_2"
        self.GET_HOT_PLATE_SAFETY_TEMPERATURE_PV = "IN_PV_3"
        self.GET_HOT_PLATE_SAFETY_TEMPERATURE_SP = "IN_SP_3"
        self.GET_VISCOSITY_TREND_PV = "IN_PV_5"
        self.SET_OPERATING_MODE = "SET_MODE_n"

        super().__init__(address, port, mode, device_name, connect_on_instantiation, soft_fail_for_testing)

    @property
    @command
    def stir_rate_pv(self):
        """
        Reads the process variable (i.e. the current) stir rate

        Returns:
            call back to send_message with a request to return and check a value
        """
        return self.send_message(self.GET_STIR_RATE_PV, True, self.valueanswer)

    @property
    @command
    def stir_rate_sp(self):
        """
        Reads the set point (target) for the stir rate

        Returns:
            call back to send_message with a request to return and check a value
        """
        return self.send_message(self.GET_STIR_RATE_SP, True, self.valueanswer)

    @stir_rate_sp.setter
    @command
    def stir_rate_sp(self, stir_rate=None):
        """
        Sets the stirrer rate and return the set point from the hot plate so the user can verify that it was successful.

        Args:
            stir_rate (int): the target stir rate of the hot plate

        Returns:
            call back to get_stirrer_rate_set_point()
        """
        try:
            # type checking of the stir rate that the user provided
            stir_rate = int(stir_rate)
        except ValueError:
            raise(ValueError("Error setting stir rate. Rate was not a valid integer \"{0}\"".format(stir_rate)))

        self.logger.debug("Setting stir rate to {0} RPM...".format(stir_rate))

        # actually sending the command
        self.send_message("{0} {1}".format(self.SET_STIR_RATE_SP, stir_rate))

    @property
    @command
    def temperature_pv(self):
        # reading the process variable
        return self.send_message(self.GET_TEMP_PV, True, self.valueanswer)

    @property
    @command
    def temperature_sp(self):
        return self.send_message(self.GET_TEMP_SP, True, self.valueanswer)

    @temperature_sp.setter
    @command
    def temperature_sp(self, temperature=None):
        """
        Sets the target temperature for sensor 1 (i.e. "medium temperature (external temperature sensor)"

        Args:
            temperature (float): the target temperature
        """
        try:
            temperature = float(temperature)
        except ValueError:
            raise(ValueError("Error setting  temperature. Value was not a valid float \"{0}\"".format(temperature)))

        self.logger.debug("Setting temperature setpoint to {0}°C...".format(temperature))

        # actually sending the command
        self.send_message("{0} {1}".format(self.SET_TEMP_SP, temperature))

    @command
    def start_heater(self):
        self.logger.debug("Starting heater...")
        return self.send_message(self.START_TEMP)

    @command
    def stop_heater(self):
        self.logger.debug("Stopping heater...")
        return self.send_message(self.STOP_TEMP)

    @command
    def start_stirrer(self):
        self.logger.debug("Starting stirrer...")
        return self.send_message(self.START_STIR)

    @command
    def stop_stirrer(self):
        self.logger.debug("Stopping heater...")
        return self.send_message(self.STOP_STIR)

    @command
    def reset_hot_plate(self):
        return self.send_message(self.RESET)

    @property
    @command
    def name(self):
        """
        Returns the name of the hot plate

        Returns:
            call back to send_message with a request to return the name
        """
        return self.send_message(self.GET_NAME, True)

    @command
    def set_watch_dog_temp(self):
        # TODO handle echo!
        pass

    @command
    def set_watch_dog_stir_rate(self):
        # TODO handle echo!
        pass

    @command
    def get_hot_plate_temp_current(self):
        pass

    @property
    @command
    def temperature_hot_plate_pv(self):
        return self.send_message(self.GET_HOT_PLATE_TEMPERATURE_PV, True, self.valueanswer)

    @property
    @command
    def temperature_hot_plate_safety_pv(self):
        """
        This is a documented function and does return values, but I cannot figure out what it's supposed to be...

        Returns:
            excellent question...
        """
        self.logger.debug("WARNING! Don't use temperature_hot_plate_safety_pv! (see docstring)")
        return self.send_message(self.GET_HOT_PLATE_SAFETY_TEMPERATURE_PV, True, self.valueanswer)

    @property
    @command
    def temperature_hot_plate_safety_sp(self):
        """
        This returns the current safety temperature set point. There is no equivalent setter function (for obvious
        safety reasons, it actually does not exist in the firmware)

        Returns:
            The current setting of the hot plate safety temperature
        """
        return self.send_message(self.GET_HOT_PLATE_SAFETY_TEMPERATURE_SP, True, self.valueanswer)

    @property
    @command
    def viscosity_trend(self):
        """
        Return the current viscosity trend. There is no equivalent setter function.

        Returns:
            The current viscosity trend.
        """
        return self.send_message(self.GET_VISCOSITY_TREND_PV, True, self.valueanswer)


if __name__ == '__main__':
    import time
    print('start')
    hp = IKARCTDigital(port="COM5", connect_on_instantiation=True)
    hp.temperature_sp = 99  # setting temperature to 100 °C
    print("temperature_pv {}".format(hp.temperature_pv))
    hp.start_heater()  # starting the heater
    time.sleep(5)
    hp.stop_heater()  # stopping heater
    hp.stir_rate_sp = 500
    hp.start_stirrer()
    time.sleep(5)
    print(hp.viscosity_trend)
    hp.stop_stirrer()
    print("temperature_hot_plate_safety_pv {}".format(hp.temperature_hot_plate_pv))
    print("temperature_hot_plate_safety_pv {}".format(hp.temperature_hot_plate_safety_pv))
    print("temperature_hot_plate_safety_sp {}".format(hp.temperature_hot_plate_safety_sp))
    while True:
        pass
