# coding=utf-8
# !/usr/bin/env python
"""
"IKA_RV10" -- API for IKA RV10 remote controllable rotary evaporator
====================================================================

.. module:: IKA_RV10
   :platform: Windows
   :synopsis: Control IKA RV10 rotary evaporator.
   :license: BSD 3-clause
.. moduleauthor:: Cronin Group 2018

(c) 2018 The Cronin Group, University of Glasgow

This provides a python class for the IKA RV 10 rotary evaporator with IKA HB 10 heating bath. The command implementation
is not based on the manual since the manual list different/wrong commands for the rotavap and no commands for the bath
at all. The correct commands were worked out in correspondence with IKA and by trial and error.

For style guide used see http://xkcd.com/1513/
"""

# system imports
import re
import serial
from time import sleep, time
from threading import Event

# Core import
from SerialLabware.serial_labware import SerialDevice, command


class IKARV10(SerialDevice):
    """
    This provides a python class for the IKA RV 10 rotary evaporator
    with IKA HB 10 heating bath.
    The command implementation is not based on the manual since the
    manual list different/wrong commands for the rotavap and no commands
    for the bath at all. The correct commands were worked out in
    correspondence with IKA and by trial and error.
    """

    def __init__(self, port=None, device_name=None, connect_on_instantiation=True, soft_fail_for_testing=False, address=None, mode=None):
        """
        Initializer of the IKARV10 class

        Args:
            port (str): The port name/number of the rotavap
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

        self.write_delay = 0.1
        self.read_delay = 0.1

        # answer patterns
        self.stranswer = re.compile(r"([0-9A-Z_]+)\r\n")
        self.intanswer = re.compile(r"(\d+) (\d)\r\n")
        self.floatanswer = re.compile(r"(\d+\.\d+) (\d)\r\n")

        # DOCUMENTED COMMANDS for easier maintenance
        self.GET_ROTATION_PV = "IN_PV_4"
        self.GET_ROTATION_SP = "IN_SP_4"
        self.SET_ROTATION_SP = "OUT_SP_4"  # 20-280 RPM
        self.GET_TEMP_PV = "IN_PV_2"
        self.GET_TEMP_SP = "IN_SP_2"
        self.SET_TEMP_SP = "OUT_SP_2"  # 0-180°C, max. T is safety temperature minus 10°C, T>90°C switches to oil mode
        self.GET_SAFETY_TEMP_SP = "IN_SP_2"
        self.SET_SAFETY_TEMP_SP = "OUT_SP_2"
        self.START_TEMP = "START_2"
        self.STOP_TEMP = "STOP_2"
        self.START_ROTATION = "START_4"
        self.STOP_ROTATION = "STOP_4"
        self.RESET = "RESET"
        self.GET_NAME = "IN_NAME"
        self.SET_NAME = "OUT_NAME"
        self.GET_SOFTWARE_VERSION = "IN_SOFTWARE"
        self.SET_INTERVAL_SP = "OUT_SP_60"  # 1-60s, "0" switches mode off
        self.SET_TIMER_SP = "OUT_SP_61"  # 1-199min, "0" switches mode off
        self.LIFT_UP = "OUT_SP_62 1"
        self.LIFT_DOWN = "OUT_SP_63 1"

        self.MAX_RPM = 280

        self.MAX_RETRIES = 10

        self.heating_on = Event()  # communicator for switching the keepalive on or off

        super().__init__(address, port, mode, device_name, connect_on_instantiation, soft_fail_for_testing)

    def keepalive(self):
        """
        Queries heating bath temperature every 2 seconds if the heating is on to keep it alive. Overrides dummy
        keepalive from parent method. This does not utilise the non_blocking_wait method because passing a property as
        callback leads to unwanted behaviour (i.e. property gets read on every loop iteration, not just
        every x seconds). self.last_time is initialised in the parent method.
        """

        # check if heater is on
        if self.heating_on.is_set():
            try:
                # monitor temperature
                temp = self.temperature_pv
                floattemp = float(temp[0])
                sleep(2)
            except ValueError:
                self.logger.exception("Oh noes! Something went wrong!")
                # stop heater when something goes wrong
                self.stop_heater()
        # when heating is off run parent "keepalive"
        else:
            sleep(0.1)

    @command
    def initialise(self):
        """
        Due to unspeakable firmware dumbfuckery both rotavap and heating bath only actually enter remote mode
        after a start command has been sent. This method starts and stops both devices to force them into
        remote mode.

        Returns:
            True if successful, False if not
        """
        self.logger.debug("Initialising IKA RV10...")
        try:
            self.start_rotation()
            self.stop_rotation()
            self.start_heater()
            self.stop_heater()
            return True
        except Exception as e:
            self.logger.critical("Error while initialising rotavap: {0}".format(e))
            return False

    @property
    @command
    def rotation_speed_pv(self):
        """
        Reads the process variable (i.e. the current) rpm

        Returns:
            call back to send_message with a request to return and check a value
        """
        return self.send_message(self.GET_ROTATION_PV, True, self.intanswer)

    @property
    @command
    def rotation_speed_sp(self):
        """
        Reads the set point (target) for the rpm

        Returns:
            call back to send_message with a request to return and check a value
        """
        return self.send_message(self.GET_ROTATION_SP, True, self.intanswer)

    @rotation_speed_sp.setter
    @command
    def rotation_speed_sp(self, rpm=None):
        """
        Sets the rotation speed and return the set point from the rotavap so the user can verify that it was successful

        Returns:
            int: the target rotation speed of the rotavap
        """
        try:
            # type checking of the rotation speed that the user provided
            rpm = int(rpm)
        except ValueError:
            raise(ValueError("Error setting rotation speed. Speed was not a valid integer: \"{0}\"".format(rpm)))

        if rpm < 0 or rpm > self.MAX_RPM:
            raise (ValueError("Error setting rotation speed. Speed was outside the limits: \"{0}\"".format(rpm)))

        self.logger.debug("Setting rotation speed to {0} RPM...".format(rpm))

        # actually sending the command
        self.send_message("{0} {1}".format(self.SET_ROTATION_SP, rpm))

    @property
    @command
    def temperature_pv(self):
        # reading the process variable
        return self.send_message(self.GET_TEMP_PV, True, self.floatanswer)

    @property
    @command
    def temperature_sp(self):
        return self.send_message(self.GET_TEMP_SP, True, self.floatanswer)

    @temperature_sp.setter
    @command
    def temperature_sp(self, temperature=None):
        """
        Sets the target temperature for the heating bath

        Args:
            temperature (float): the target temperature
        """
        try:
            temperature = int(temperature)
        except ValueError:
            raise(ValueError("Error setting temperature. Value was not a valid float \"{0}\"".format(temperature)))

        self.logger.debug("Setting heating bath temperature to {0}°C...".format(temperature))

        self.send_message("{0} {1}".format(self.SET_TEMP_SP, temperature))

    @command
    def start_heater(self):
        self.logger.debug("Starting heater...")
        self.heating_on.set()
        return self.send_message(self.START_TEMP)

    @command
    def stop_heater(self):
        self.logger.debug("Stopping heater...")
        self.heating_on.clear()
        return self.send_message(self.STOP_TEMP)

    @command
    def start_rotation(self):
        self.logger.debug("Starting rotation...")
        return self.send_message(self.START_ROTATION)

    @command
    def stop_rotation(self):
        self.logger.debug("Stopping rotation...")
        return self.send_message(self.STOP_ROTATION)

    @command
    def lift_up(self):
        self.logger.debug("Lifting up...")
        return self.send_message(self.LIFT_UP)

    @command
    def lift_down(self):
        self.logger.debug("Lifting down...")
        return self.send_message(self.LIFT_DOWN)

    @command
    def reset_rotavap(self):
        self.logger.debug("Resetting rotavap...")
        return self.send_message(self.RESET)

    @property
    @command
    def name(self):
        """
        Returns the name of the rotavap

        Returns:
            call back to send_message with a request to return the name
        """
        return self.send_message(self.GET_NAME, True)

    # setting a name doesn't seem to work
    # @name.setter
    # def name(self, name=None):
    #     """
    #     Sets the name of the rotavap to "name". Resets to default (self.IKA_default_name) if no name is passed.
    #         Warns that names longer than 6 characters get truncated upon restart of the rotavap.
    #     :param name: (string) the new name
    #     """
    #     if name is None:
    #         name = self.IKA_default_name
    #     if len(name) > 6:
    #         self.logger.debug("Warning name will be shortened to \"{}\" by the rotary evaporator after restart.".format(name[0:6]))
    #     self.send_message("{0} {1}".format(self.SET_NAME, name))

    @property
    @command
    def software_version(self):
        """
        Returns the software version of the firmware
        !!!WARNING!!! Despite being documented this does not seem to work as intended, it just returns an empty string

        Returns:
            (supposed to...) software version of the firmware
        """
        return self.send_message(self.GET_SOFTWARE_VERSION, True)

    @property
    @command
    def safety_temp(self):
        return self.send_message(self.GET_SAFETY_TEMP_SP, True, self.floatanswer)

    @safety_temp.setter
    @command
    def safety_temp(self, temperature):
        """
        Sets the safety temperature for the heating bath

        Args:
            temperature (float): the safety temperature
        """
        try:
            temperature = float(temperature)
        except ValueError:
            raise(ValueError("Error setting heating bath temperature. Value was not a valid float \"{0}\"".format(temperature)))
        self.send_message("{0} {1}".format(self.SET_SAFETY_TEMP_SP, temperature))

    @command
    def set_interval(self, interval):
        """
        Sets the interval length in seconds for the interval mode. Setting this to 0 stops the function

        Args:
            interval (int): the interval in seconds (1-60)
        """
        try:
            interval = float(interval)
        except ValueError:
            raise(ValueError("Error setting interval time. Value was not a valid integer \"{0}\"".format(interval)))
        self.logger.debug("Setting interval time to {0}s...".format(interval))
        self.send_message("{0} {1}".format(self.SET_INTERVAL_SP, interval))

    @command
    def set_timer(self, time_setpoint):
        """
        Sets the time in minutes for the timer mode. Setting this to 0 stops the function

        Args:
            time_setpoint (int): the time in minutes (1-199)
        """
        try:
            time_setpoint = float(time_setpoint)
        except ValueError:
            raise (ValueError("Error setting timer. Value was not a valid integer \"{0}\"".format(time_setpoint)))
        self.send_message("{0} {1}".format(self.SET_TIMER_SP, time_setpoint))


if __name__ == '__main__':
    rv = IKARV10(port="COM5", connect_on_instantiation=True)
    sleep(1)
    rv.initialise()
    rv.temperature_sp = 30  # setting temperature to 30 °C
    print("Temp {}".format(rv.temperature_pv))
    rv.start_rotation()  # starting the heater
    # rv.stop_heater()  # stopping heater
    sleep(1)
    print("Safety temp {}".format(rv.safety_temp))
    print("Temp {}".format(rv.temperature_pv))
    print("Speed {}".format(rv.rotation_speed_pv))
    # print("Name {}".format(rv.name))
    # print("Ver {}".format(rv.software_version))
    while True:
        pass
