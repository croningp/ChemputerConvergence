# coding=utf-8
# !/usr/bin/env python
"""
"Heidolph_HeiTORQUE_100" -- API for Heidolph HeiTORQUE100 control remote controllable overhead stirrer
=====================================================================================================

.. module:: Hei_Torque_100_Control_Stirrer
   :platform: Windows
   :synopsis: Control Heidolph HeiTORQUE100 control overhead stirrer
   :license: BSD 3-clause
.. moduleauthor:: Artem Leonov <Artem.Leonov@glasgow.ac.uk>

(c) 2018 The Cronin Group, University of Glasgow

This provides a python class for the Heidolph HeiTORQUE100 control overhead stirrer.

For style guide used see http://xkcd.com/1513/
"""

# system imports
import re
from time import sleep
import logging

# Core import
from SerialLabware.serial_labware import SerialDevice, command


class HeiTORQUE_100(SerialDevice):
    """
    This provides a python class for the overhead stirrer Heidolph Hei-TORQUE 100
    based on the english translation of the original operaion manual v1.5 from 09/2017
    """
    def __init__(self, port=None, device_name=None, connect_on_instantiation=True, soft_fail_for_testing=False, address=None, mode=None):
        """
        Initializer of the HeiTORQUE_100 class

        Args:
            port (str): The port name/number of the stirrer
            name (str): A descriptive name for the device, used mainly in debug prints
            connect_on_instantiation (bool): (optional) determines if the connection is established on instantiation of
                the class. Default: On
            soft_fail_for_testing (bool): (optional) determines if an invalid serial port raises an error or merely
                logs a message. Default: Off
        """

        # serial settings
        # all settings are at default, 9600 Baud, 8N1, no flow control
        self.timeout = 1
        self.command_termination = '\r\n'

        self.write_delay = 0.1
        self.read_delay = 0.1

        # answer patterns
        self.query_answer = re.compile("([A-Z]{3}): ([0-9]+)\r\n\r\n")  # most answers, except for status and setpoint
        self.setpoint_answer = re.compile("R([0-9]+)\r\n([A-Z]{3}): ([0-9]+)\r\n")  # reply to setting the RPM
        self.status_answer = re.compile("([A-Z]{3}): (.*)\r\n")  # most answers, except for status and setpoint
        self.error_answer = re.compile("(\w+\W) (.*\W)\r\n") # pattern for the error answers

        # since the current overhead stirrer doesn't support the previously used command sequence:
        # get_speed -> set_speed -> start_stirring
        # the default value for the stirring has to be setted to maintain compatibility with other stirrer API
        self._preset_rpm = 200

        # DOCUMENTED COMMANDS for easier maintenance
        self.set_rpm = "R"  # Rxxxx (1-4 digits) sets and ***STARTS*** stirring at the RPM value. limits are 30-1000 rpm
        self.delete_error = "C"  # delete the "Overload" error message
        self.remote_off = "D"  # deactivate the remote control to operate the device manually 
        self.set_reference = "N"  # set the current torque to zero (for calibration purposes)

        self.get_rpm = "r"  # queries current RPM
        self.get_setpoint = "s"  # queries setpoint
        self.get_torque = "m"  # queries torque
        self.get_error = "f"  # No Error! / Motor Error! / Motor Temperature! / Stopped Manually! / Overload!
        self.indicate_msg = 'M' # device identification: returns 'M' and start flashing the display

        super().__init__(address, port, mode, device_name, connect_on_instantiation, soft_fail_for_testing)


    @property
    @command
    def stir_rate_pv(self):
        """
        Returns the stir rate process value

        Returns:
            rpm (int): RPM process value
        """
        rpm = self.send_message(self.get_rpm, get_return=True, return_pattern=self.query_answer, multiline=True)
        self.logger.debug('the current speed is {}'.format(rpm))
        return int(rpm[1])

    @property
    @command
    def stir_rate_sp(self):
        """
        Returns the stir rate setpoint

        Returns:
            rpm (int): RPM setpoint
        """
        return self._preset_rpm


    @stir_rate_sp.setter
    @command
    def stir_rate_sp(self, rpm):
        """
        Sets the target rpm for the stirrer.

        Args:
            rpm (int): RPM setpoint
        """
        try:
            # type checking of the stir rate that the user provided
            rpm = int(rpm)
        except ValueError:
            raise(ValueError("Error setting stir rate. Rate was not a valid integer \"{0}\"".format(rpm)))
        self.logger.debug("Setting stir rate to %s RPM...", rpm)
        # Checking that requested speed is in range
        if rpm <= 30:
            rpm = 30
            self.logger.warning('Requested speed is too low, %s stirrer stirring speed is set to %s rpm', self.device_name, rpm)
        elif rpm > 800:
            rpm = 800
            self.logger.warning('Requested speed is too high, %s stirrer stirring speed is set to %s rpm', self.device_name, rpm)
        # No change needed
        if rpm == self._preset_rpm:
            self.logger.info('%s stirrer stirring speed is already %s rpm', self.device_name, self._preset_rpm)
        else:
            # Update value
            self._preset_rpm = rpm
            reply_msg = self.send_message('{}{}'.format(self.set_rpm, self._preset_rpm), get_return=True, return_pattern=self.setpoint_answer, multiline=True)
            self.logger.info('%s is now stirring at %s rpm', self.device_name, reply_msg[0])


    @command
    def start_stirrer(self):
        """Start the stirrer"""
        self.logger.debug('{} start stirring at {} rpm'.format(self.device_name, self._preset_rpm))
        reply_msg = self.send_message('{}{}'.format(self.set_rpm, self._preset_rpm), get_return=True, return_pattern=self.setpoint_answer, multiline=True)
        self.logger.debug('{} started stirring at {} rpm'.format(self.device_name, reply_msg[0]))
        self.logger.debug(str(reply_msg))

    @command
    def stop_stirrer(self):
        """Stops the stirrer"""
        self.logger.debug('{} stop stirring'.format(self.device_name))
        reply_msg = self.send_message("{0}{1:04}".format(self.set_rpm, 0), get_return=True, return_pattern=self.setpoint_answer, multiline=True)
        if reply_msg[0] != '0000':
            self.send_message(self.remote_off, True)
            raise Exception('{} has not stopped, check manually'.format(self.device_name))

    @command
    def get_status(self):
        """ Returns the error code of the stirrer"""
        status = self.send_message(self.get_error, get_return=True, return_pattern=self.error_answer, multiline=True)
        return status[1].strip()

    @command
    def identify(self):
        self.send_message(self.indicate_msg, True)

    @command
    def clear_errors(self):
        self.send_message(self.delete_error, True)


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	left = HeiTORQUE_100(address='192.168.1.204', device_name='left')
	right = HeiTORQUE_100(port='COM4', device_name='right')
	left.identify()
	right.identify()
	sleep(5)
	left.stir_rate_sp = 100
	right.stir_rate_sp = 100
	left.start_stirrer()
	right.start_stirrer()
	sleep(10)
	left.stop_stirrer()
	right.stop_stirrer()
