#!/usr/bin/python
"""
"Tricontinent_C3000_C3000MP" -- API for Tricontinent C3000 and C3000MP syringe pumps
===================================

.. module:: Tricontinent_C3000_C3000MP
   :platform: Windows
   :synopsis: Control Tricontinent C3000 and C3000MP syringe pumps
   :license: BSD 3-clause
.. moduleauthor:: Sergey Zalesskiy <sergey.zalesskiy@glasgow.ac.uk>

(c) 2018 The Cronin Group, University of Glasgow

This provides a python class for the Tricontinent C3000 and C3000MP syringe pumps. Command implementation is based on the
Product Manual (Publication 8694-12 E), chapter 5 "Operating instructions" and chapter 9, section 3, "Data Terminal (DT) protocol"
"""

# system imports
# FIXME
# This should be removed / replaced by facade
import serial

# Core import
from SerialLabware.serial_labware import SerialDevice, command
from .C3000_commands import C3000Error, C3000ProtocolError, C3000_commands_DT


class C3000(SerialDevice):
    """Control class for C3000 pump"""

    def __init__(self, port=None, device_name=None, connect_on_instantiation=True, soft_fail_for_testing=False, address=None, mode=None):
        """Class constructor
        Keyword Arguments:
            port {str} -- Serial port name (default: {None}).
            device_name {str} -- Device name, used for logging in SerialDevice (default: {None}).
            soft_fail_for_testing {bool} -- Another weird thingie to comply with Sebastian's code. Not used (default: {False}).
        Raises:
            C3000ProtocolError -- Communication protocol error including protocol-specific error messages as per pump manual.
            C3000Error -- Generic error.
        """

        # Set name
        if device_name is None: 
            device_name = self.__class__.__name__
        self.device_name = device_name

        # Set address
        self.address = None
        
        # Set port
        self.port = port

        # Load commands from helper class
        self.cmd = C3000_commands_DT

        # Set serial interface parameters
        self.baudrate = 9600
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.rtscts = False
        self.command_termination = self.cmd.SUFFIX
        self.write_delay = 0.5
        self.read_delay = 0.5
        self.timeout = 5

        super().__init__(address, port, mode, device_name, connect_on_instantiation, soft_fail_for_testing)


    def map_address(self, value):
        """Maps rotary switch position to ASCII address.
        Arguments:
            value {int or str} -- Value of the rotary switch position on the back of the pump.
        Returns:
            str -- ASCII value of the pump address.
        """
        
        if value is None:
            raise C3000ProtocolError("No address supplied!") from None
        try:
            return self.cmd.VALID_ADDRESSES[str(value)]
        except KeyError:
            raise C3000ProtocolError("Invalid address supplied!") from None

    # This function  is currently needed to cope with Sebastian's "polymorphic" return-type style of send_message() - it can either return int or bool or str
    # FIXME
    def check_reply(self, reply):
        """Checks whether reply type got from send_message() is actually string.
        Arguments:
            reply {whatever} -- Raw reply from the pump.
        """
        
        if not isinstance(reply, str) or len(reply) < 3:
            raise C3000Error("Unexpected reply from the pump - {}".format(reply))
        return reply

    def strip_reply(self, reply):
        """Cuts out actual DT protocol reply removing the header+status byte and footer.
        Arguments:
            reply {str} -- Raw reply from the pump (e.g.'/0`3\x03').
        Returns:
            str -- Reply body (e.g. '3' for the raw reply above).
        """

        return reply[3:-1]

    def check_error_code(self, reply):
        """Checks error bits in the status byte of the pump reply.
        Arguments:
            reply {str} -- Raw reply from the pump.
        Raises:
            C3000ProtocolError -- Protocol-specific error in case any error bits are active. See C3000_C3000MP_commands for error codes.
        """
        
        # First, ensure that it's actually string, thanks to STS.
        reply = self.check_reply(reply)
        # Status byte is the 3rd byte of reply string & we need it's numeric representation
        status_byte = ord(reply[2])
        # Error code is contained in 4 right-most bytes, so we need to chop off the rest
        error_code = status_byte & 0b1111
        # No error
        if error_code == 0:
            return None
        else:
            try:
                raise C3000ProtocolError(self.cmd.ERROR_CODES[error_code])
            except KeyError:
                # This shouldn't really happen, means that pump replied with error code not in the ERROR_CODES dictionary (which completely copies the manual)
                raise C3000ProtocolError("Unknown error! Status byte: {}".format(bin(status_byte)))
    
    def check_busy_bit(self, reply):
        """Checks busy bit in the status byte of the pump reply.
        Arguments:
            reply {str} -- Raw reply from the pump.
        Returns:
            int -- Busy bit value.
        """
        
        reply = self.check_reply(reply)
        # Status byte is the 3rd byte of reply string & we need it's numeric representation
        status_byte = ord(reply[2])
        # Busy/idle bit is 6th bit of the status byte. 0 - busy, 1 - idle
        if status_byte & 1<<5 == 0:
            return 0
        else:
            return 1
    
    def send_message(self, message, get_return=True, return_pattern=None, multiline=False):
        """Overloaded method from SerialDevice. Always asks for reply (because Triconts always spit reply back) & checks reply for errors
        Arguments:
            message {str} -- Full command (with prefix and pump address) to send (e.g. '/1ZR').
        Keyword Arguments:
            get_return {bool} -- Defines whether we should wait for reply from pump and return reply back (default: {True}).
            return_pattern {[type]} -- Regex pattern for in-built processing of the reply somewhere in SerialDevice (default: {None}).
            multiline {bool} -- Defines whether we expect multiline reply (default: {False}).
        Returns:
            str -- Raw reply from the pump.
        """
        
        reply = super().send_message(message, get_return, return_pattern, multiline)
        self.check_error_code(reply)
        return reply

    @command
    def init_pump_full(self, valve_enumeration_direction="CW", input_port=None, output_port=None, run=True, address=None):
        """Runs pump initialization. This function is heavily commented, the rest of commands follow pretty much the same flow.

        Keyword Arguments:
            valve_enumeration_direction {str} -- Defines whether valve numbering would be CW (1 on the left) or CCW (1 on the right) counting from the syringe (default: {"CW"}).
            input_valve {int} -- Which port to use as input during initialization sequence (default: {None})
            output_valve {[type]} -- Which port to use as output during initialization sequence (default: {None})
            run {bool} -- Defines whether the pump will execute command immediately or just buffer it (default: {True}).
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Raises:
            C3000ProtocolError -- Any other direction except CW or CCW was provided.
        Returns:
            str -- Raw reply from the pump.
        """
        
        # Map switch position to ASCII address
        address = self.map_address(address)
        
        # Select appropriate command depending on the direction
        if valve_enumeration_direction == "CW":
            cmd = self.cmd.PREFIX + address + self.cmd.INIT_ALL_CW
        elif valve_enumeration_direction == "CCW":
            cmd = self.cmd.PREFIX + address + self.cmd.INIT_ALL_CCW
        else:
            raise C3000ProtocolError("Invalid direction for valve initialization provided!")

        # Initialization arguments. First - plunger initialization power(we're not using it).
        # Second - number of input port for initialization (0-default).
        # Third - number of output port for initialization (0 - default)
        args = [0, 0, 0]

        # Check if we are asked to use specific input/output ports. Otherwise they will be first(I) and last(O) for CW init or last(I) and first(O) for CCW init
        if input_port is not None:
            try:
                #Check if we were given a valid port number. This might still return an error, cause the function doesn't know which valve is installed - 3-way, 6-way or some other
                _ = self.cmd.VLV_POS.index("I"+str(input_port))
                args[1] = input_port
            except ValueError:
                raise C3000ProtocolError("Invalid input port number was provided!") from None
        if output_port is not None:
            try:
                #Check if we were given a valid port number. This might still return an error, cause the function doesn't know which valve is installed - 3-way, 6-way or some other
                _ = self.cmd.VLV_POS.index("O"+str(output_port))
                args[2] = output_port
            except ValueError:
                raise C3000ProtocolError("Invalid output port number was provided!") from None
        
        # Glue arguments to the command they should be comma-separated list (0,0,0)
        cmd += ",".join(str(a) for a in args)
        
        # Append run flag if needed
        if run is True:
            cmd += self.cmd.CMD_RUN
        return self.send_message(cmd)

    @command
    def move_plunger_absolute(self, position, set_busy=True, run=True, address=None):
        """Makes absolute plunger move.
        Arguments:
            position {int} -- Plunger position in stepper motor increments (0-3000 for C3000 in normal resolution mode).
        Keyword Arguments:
            set_busy {bool} -- Defines whether the pump sets busy bit while making the move (default: {True}).
            run {bool} -- Defines whether the pump will execute command immediately or just buffer it (default: {True}).
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Returns:
            str -- Raw reply from the pump.
        """

        address = self.map_address(address)
        if set_busy is True:
            cmd = self.cmd.SYR_POS_ABS
        else:
            cmd = self.cmd.SYR_POS_ABS_NOBUSY
        cmd = self.cmd.PREFIX + address + cmd + str(position)
        if run is True:
            cmd += self.cmd.CMD_RUN
        return self.send_message(cmd)

    @command
    def dispense_relative(self, increments, set_busy=True, run=True, address=None):
        """Makes relative dispense.
        Arguments:
            increments {int} -- Dispense volume in stepper motor increments.
        Keyword Arguments:
            set_busy {bool} -- Defines whether the pump sets busy bit while making the move (default: {True}).
            run {bool} -- Defines whether the pump will execute command immediately or just buffer it (default: {True}).
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Returns:
            str -- Raw reply from the pump.
        """
        
        address = self.map_address(address)
        if set_busy is True:
            cmd = self.cmd.SYR_SPIT_REL
        else:
            cmd = self.cmd.SYR_SPIT_REL_NOBUSY
        cmd = self.cmd.PREFIX + address + cmd + str(increments)
        if run is True:
            cmd += self.cmd.CMD_RUN
        return self.send_message(cmd)

    @command
    def aspirate_relative(self, increments, set_busy=True, run=True, address=None):
        """Makes relative aspiration.
        Arguments:
            increments {int} -- Aspiration volume in stepper motor increments.
        Keyword Arguments:
            set_busy {bool} -- Defines whether the pump sets busy bit while making the move (default: {True}).
            run {bool} -- Defines whether the pump will execute command immediately or just buffer it (default: {True}).
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Returns:
            str -- raw reply from the pump
        """

        address = self.map_address(address)
        if set_busy is True:
            cmd = self.cmd.SYR_SUCK_REL
        else:
            cmd = self.cmd.SYR_SUCK_REL_NOBUSY
        cmd = self.cmd.PREFIX + address + cmd + str(increments)
        if run is True:
            cmd += self.cmd.CMD_RUN
        return self.send_message(cmd)

    @command
    def set_ramp_slope(self, ramp, address=None):
        """Sets slope of acceleration/deceleration ramp for the syringe motor.
        Arguments:
            ramp {str} -- Ramp code. Check manual for ramp <-> steps/sec^2 relations.
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Returns:
            str -- Raw reply from the pump.
        """
        if ramp not in self.cmd.RAMP_SLOPE_MODES:
            raise C3000ProtocolError("Invalid ramp mode provided!")
        address = self.map_address(address)
        cmd = self.cmd.PREFIX + address + self.cmd.SET_RAMP_SLOPE + str(ramp) + self.cmd.CMD_RUN
        return self.send_message(cmd)
    
    @command
    def set_start_velocity(self, velocity, address=None):
        """Sets starting velocity for the syringe motor.        
        Arguments:
            velocity {str} -- Velocity in steps/sec.
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Returns:
            str -- Raw reply from the pump.
        """

        address = self.map_address(address)
        cmd = self.cmd.PREFIX + address + self.cmd.SET_START_VEL + str(velocity) + self.cmd.CMD_RUN
        return self.send_message(cmd)

    @command
    def set_max_velocity(self, velocity, address=None):
        """Sets maximum velocity (top of the ramp) for the syringe motor.
        Arguments:
            velocity {str} -- Maximum velocity in increments/second.
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Raises:
            C3000ProtocolError -- Wrong speed code provided.
        Returns:
            str -- Raw reply from the pump.
        """

        address = self.map_address(address)
        cmd = self.cmd.PREFIX + address + self.cmd.SET_MAX_VEL + str(velocity) + self.cmd.CMD_RUN
        return self.send_message(cmd)

    @command
    def set_max_velocity_code(self, velocity_code, address=None):
        """Sets maximum velocity (top of the ramp) for the syringe motor.
        Arguments:
            velocity_code {str} -- Maximum velocity code 0..40.
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Raises:
            C3000ProtocolError -- Wrong speed code provided.
        Returns:
            str -- Raw reply from the pump.
        """

        address = self.map_address(address)
        velocity_code = str(velocity_code)
        if velocity_code not in self.cmd.SPEED_MODES:
            raise C3000ProtocolError("Invalid speed code provided!") from None
        cmd = self.cmd.PREFIX + address + self.cmd.SET_MAX_VEL_CODE + str(velocity_code) + self.cmd.CMD_RUN
        return self.send_message(cmd)
    
    @command
    def set_stop_velocity(self, velocity, address=None):
        """Sets stopping velocity for the syringe motor.        
        Arguments:
            velocity {str} -- Stopping velocity in steps/sec.
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Returns:
            str -- Raw reply from the pump.
        """
        address = self.map_address(address)
        cmd = self.cmd.PREFIX + address + self.cmd.SET_STOP_VEL + str(velocity) + self.cmd.CMD_RUN
        return self.send_message(cmd)
    
    @command
    def set_resolution_mode(self, resolution_mode, address=None):
        """Sets plunger resolution mode.
        Arguments:
            resolution_mode {str} -- Resolution mode code (N0 - 3000 steps/stroke, N1 - 24000 steps/stroke).
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Raises:
            C3000ProtocolError -- Wrong resolution code provided
        Returns:
            str -- Raw reply from the pump.
        """

        address = self.map_address(address)
        if resolution_mode not in self.cmd.RESOLUTION_MODES.keys():
            raise C3000ProtocolError("Invalid resolution mode {} provided!".format(resolution_mode)) from None
        cmd = self.cmd.PREFIX + address + self.cmd.SET_RES_MODE + str(resolution_mode) + self.cmd.CMD_RUN
        return self.send_message(cmd)

    @command
    def set_valve_type(self, valve_type, address=None):
        """Sets valve type. This command requires power-cycle to activate new settings!
        Arguments:
            valve_type {str} -- Valve type from C3000_C3000MP_commands.VLV_TYPES dictionary.
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Raises:
            C3000ProtocolError -- Valve type requested not found in C3000_C3000MP_commands.VLV_TYPES dictionary.
        Returns:
            str -- Raw reply from the pump.
        """

        address = self.map_address(address)
        try:
            valve_type_requested = self.cmd.VLV_TYPES[valve_type]
        except KeyError:
            raise C3000ProtocolError("Invalid valve type provided!") from None
        cmd = self.cmd.PREFIX + address + self.cmd.SET_PUMP_CONF + valve_type_requested
        return self.send_message(cmd)
    
    @command
    def set_valve_position(self, position, rotation_direction="CW", address=None):
        """Moves valve to the position requested.
        Arguments:
            valve_position {int} -- Valve position requested.
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
            rotation_direction {str} -- Which direction, CW or CCW to go to reach required valve position. Not really useful. (default: {"CW"}).
        Raises:
            C3000ProtocolError -- Valve position requested not found in C3000_C3000MP_commands.VLV_POS.
        Returns:
            str -- Raw reply from the pump.
        """

        address = self.map_address(address)
        # Check if direction is valid
        if rotation_direction == "CW":
            rotation_direction = self.cmd.VLV_ROT_CW
        elif rotation_direction == "CCW":
            rotation_direction = self.cmd.VLV_ROT_CCW
        else:
            raise C3000ProtocolError("Invalid valve rotation direction provided!")

        # Glue together rotation command and position, e.g. I+1=I1
        rotation_command = rotation_direction + str(position)

        # Check if we got something sensible (e.g. I1, not I20)
        try:
            rotation_command = self.cmd.VLV_POS[self.cmd.VLV_POS.index(rotation_command)]
        except ValueError:
            raise C3000ProtocolError("Invalid valve position provided!") from None
        cmd = self.cmd.PREFIX + address + rotation_command + self.cmd.CMD_RUN
        return self.send_message(cmd)

    @command
    def is_pump_busy(self, address=None):
        """Runs status request command and checks if busy bit is set in the reply.
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Returns:
            bool -- True if pump busy.
        """

        address = self.map_address(address)
        cmd = self.cmd.PREFIX + address + self.cmd.GET_STATUS
        if self.check_busy_bit(self.send_message(cmd)) == 0:
            return True
        else:
            return False

    @command
    def is_pump_initialized(self, address=None):
        """Checks if pump has been successfully initialized.
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Returns:
            bool -- True if pump has been successfully initialized.
        """

        address = self.map_address(address)
        cmd = self.cmd.PREFIX + address + self.cmd.GET_INIT_STATUS
        reply = self.strip_reply(self.send_message(cmd))
        if reply == "1":
            return True
        else:
            return False

    @command
    def get_pump_configuration(self, address=None):
        """Reads pump EEPROM configuration.
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Returns:
            list -- List of EEPROM parameters.
        """

        address = self.map_address(address)
        cmd = self.cmd.PREFIX + address + self.cmd.GET_EEPROM_DATA
        reply = self.strip_reply(self.send_message(cmd))
        parameters = reply.split(",")
        return parameters
    
    @command
    def get_plunger_position(self, address=None):
        """Returns absolute plunger position.
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Returns:
            int -- Plunger position in increments
        """
        
        address = self.map_address(address)
        cmd = self.cmd.PREFIX + address + self.cmd.GET_SYR_POS
        reply = self.strip_reply(self.send_message(cmd))
        return int(reply)

    @command
    def get_valve_position(self, address=None):
        """Reads current position of the valve
        Keyword Arguments:
            address {int or str} -- Value of the rotary switch position on the back of the pump (default: {None}).
        Returns:
            str -- Current position of the valve (port number or port name depending on how pump was configured - check set_valve_type and docs related to U commands).
        """
        address = self.map_address(address)
        cmd = self.cmd.PREFIX + address + self.cmd.GET_VLV_POS
        return self.strip_reply(self.send_message(cmd))
