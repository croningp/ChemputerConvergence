# coding=utf-8
# !/usr/bin/env python
"""
"conductivity_sensor" -- API for Cronin conductivity sensor
===================================

.. module:: conductivity_sensor
   :platform: Windows
   :synopsis: 60W heating pad with temperature sensors.
   :license: BSD 3-clause
.. moduleauthor:: S. Rohrbach <Simon.Rohrbach@glasgow.ac.uk>

(c) 2019 The Cronin Group, University of Glasgow

A 60 W heating pad (RS Components stock code: 798-3753) is powered with a 12 V source and controlled via an arduino due. 
The arduino board receives temperature feed-back from two DS18B20 temperature sensors (RS Compontenst order number: 540-2805). 
The operating range is room temperature to 105 °C taking in account a 20 °C safty margin at the high temperature end for the temperature sensor (designed for the temperature range -55 °C to +125 °C).
The arduino runs a modified PID feedback loop to keep the set temperature. 
"""

# System imports
import re
import serial
import logging
import time as t

# Additional module imports
from SerialLabware.serial_labware import SerialDevice, command

class HeatingPad(SerialDevice):
    """
    This provides a python class for the Cronin heating pad.
    """

    def __init__(self, port=None, device_name=None, connect_on_instantiation=True, soft_fail_for_testing=False, address=None, mode=None):
        """
        Initializer of the HeatingPad class

        Args:
            port (str): The com-port as a string inn the format COMX where X is the port number
            device_name (str): A descriptive name for the device, used mainly in debug prints
            soft_fail_for_testing (bool): (optional) determines if an invalid serial port raises an error or merely logs a message. Default: False
        """
        # Serial settings
        self.baudrate = 9600
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.rtscts = True

        # I/O Settings
        self.write_delay = 0.8
        self.read_delay = 0.8

        # Answer patterns - expected valid answers are single integers and floating point numbers. No regex is required in this module as only bare integers and floating point numbers are returned from the device. 
        #self.getanswer = re.compile("[-+]?([0-9]*[.])?[0-9]+") 
        
        # Commands
        self.GET_TEMP_1 = "get_temp_1"          # Asks for the temperatur reading from sensor 1 (in the standard built this sensor is directly attached to the heating pad)
        self.GET_TEMP_2 = "get_temp_2"          # Asks for the temperatur reading from sensor 2 (in the standard built this sensor is not direclty used and measures the ambient temperautre)
        self.GET_SET_TEMP = "get_set_temp"      # Asks for the target temperature
        self.GET_IS_TEMP = "get_is_temp"        # Asks for the last reading of the sensor at the heating pad without actually trigger a new measurement (frequent measurements can artificially increase the temperature of the sensor).
        self.GET_PWM = "get_pwm"                # Asks for the pwm level. The pwm level / 255 * 60 W gives an approximation for the current heating power output. 

        self.SET_TEMP = "set_temp"              # Sets the target temperature. 
        self.START = "start"                    # Starts heating
        self.STOP = "stop"                      # Stops heating

        super().__init__(address, port, mode, device_name, connect_on_instantiation, soft_fail_for_testing)

        if connect_on_instantiation:
            self.open_connection()
            # Temporary delay for the device to settle down before the receiving the next command

        self.logger = logging.getLogger("main_logger.heating_pad_logger")

    def open_connection(self):
        super().open_connection()
        # Temporary delay for the device to settle down before the receiving the next command
        t.sleep(1)
    
    @command
    def send_request(self, message): 
        message += '\n'
        return self.send_message(message, get_return=True, return_pattern=None, multiline=False)

# GETter functions

    def get_temp(self, sensor):
        """
        Reads the temperature from sensor 2. In the default configuration this sensor is not used and just measures the ambient temperature. 

        Returns:
            A float number. Typical error codes are 300, 400, 85, 127. These are not handeled as yet. 
        """
        # TODO Handel temperature sensor error codes

        if (sensor == 1):
            message = self.GET_TEMP_1
        elif (sensor == 2):
            message = self.GET_TEMP_2
        else:
            return "invalid request"

        return float(self.send_request(message))

    def get_is_temp(self):
        """
        Returns the last reading of the temperautre at the heating pad without re-measuring it (frequent measurements can artificially increase the temperature of the sensor). 

        Returns:
            A float number. Typical error codes are 300, 400, 85, 127. These are not handeled as yet. 
        """
        # TODO Handel temperature sensor error codes
        return float(self.send_request(self.GET_IS_TEMP))

    def get_set_temp(self):
        """
        Reads the current target temperature. 

        Returns:
            A float number. The return value -999 means that no target temperature has been set yet. 
        """
        return float(self.send_request(self.GET_SET_TEMP))

    def get_pwm(self):
        """
        Reads the current target temperature. 

        Returns:
            An int number in range 0 - 255. Return value / 255 * 60 W gives an approximation for the heating power output.  
        """
        return  int(self.send_request(self.GET_PWM))

#SETter functions    

    def set_temp(self, target_temp):
        """
        Reads the current target temperature. 

        Returns:
            An int number in range 0 - 255. Return value / 255 * 60 W gives an approximation for the heating power output.  
        """
        return float(self.send_request(self.SET_TEMP + ' ' + str(target_temp)))

    def start(self):
        """
        Swtiches ON the heating. 
        """
        return bool(self.send_request(self.START))

    def stop(self):
        """
        Swtiches OFF the heating. 
        """
        return bool(self.send_request(self.STOP))
    
#Other functions
    def wait_for_heating_pad_temp(self):
        """
        Waits until the temperature form the sensor at the heating pad is within +/- 0.5 °C of the target temperature. Does not account for overshooting. 

        Returns: 
            True if the target temp criteria is reached. 
        """
        set_tmp = self.get_set_temp()

        self.logger.info("Waiting for the heating pad to reach the target temperature of " + str(set_tmp) + " °C.\n Time Since Start (s) | Is Temp (°C) | Set Temp (°C) | Power (W) | Ext Temp (°C)\n")
        seconds = t.time()
        
        while (True): 
            is_tmp = self.get_is_temp()
            tmp_2 = self.get_temp(2)
            current_pwm = self.get_pwm() / 255 * 60.0
            self.logger.info("%21d |%13.2f |%14.2f |%10d |%13.2f " % (t.time() - seconds, float(is_tmp), float(set_tmp), int(current_pwm), float(tmp_2)))

            if (abs(set_tmp - is_tmp) <= 0.5):
                self.logger.info("Target temperature reached!\n")
                break

        return True

if __name__ == '__main__':
    hp = HeatingPad(port="COM9")
    
    print("\nHit \"ctrl-c\" to stop.\n")
    print(" Time Since Start (s) | Is Temp (°C) | Set Temp (°C) | Power (W) | Ext Temp (°C)")

    hp.set_temp(60)
    hp.start()
    seconds = t.time()

    while(True):
        try:  
            is_tmp = hp.get_is_temp()
            tmp_2 = hp.get_temp(2)
            set_tmp = hp.get_set_temp()
            current_pwm = hp.get_pwm() / 255 * 60.0

            print("%21d |%13.2f |%14.2f |%10d |%13.2f " % (t.time() - seconds, float(is_tmp), float(set_tmp), int(current_pwm), float(tmp_2)))

        except KeyboardInterrupt:
            # TODO test that the heater is properly switched off. 
            break
            
    hp.stop()   
   
    print("\nSwitch off external power source.")

