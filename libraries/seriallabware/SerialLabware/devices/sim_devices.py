import logging


class SimSerialDevice:
    def __init__(self, port=None, address=None, name=None, **kwargs):
        self.port = port
        self.address = address
        self.device_name = name

        self.logger = logging.getLogger("main_logger.sim_logger")
        self.logger.info(f"Received {self.identifier} (port = {self.port})")

    def wait_until_ready(self):
        self.logger.debug(f"{self.identifier} - Waiting until ready.")

    @property
    def identifier(self):
        return f"{self.__class__.__name__} {self.device_name}"


class SimConductivitySensor(SimSerialDevice):
    def __init__(self, port=None, device_name=None):
        super().__init__(port, device_name)

    @property
    def conductivity(self):
        return 0

    @property
    def conductivity_multiple(self):
        return (0, 0)

class SimHeatingPad(SimSerialDevice):
    def __init__(self, port=None, device_name=None, connect_on_instantiation=True, soft_fail_for_testing=False, address=None, mode=None):
        super().__init__(port, device_name)

    def open_connection(self):
        return True
    
    def send_request(self, message): 
       return message

    def get_temp(self, sensor):
        return sensor

    def get_pwm(self):
        return  True

    def set_temp(self, target_temp):
        return target_temp

    def start(self):
        return True

    def stop(self):
        return True
    
    def wait_for_heating_pad_temp(self):
        return True

class SimShakerStirrer(SimSerialDevice):
    def __init__(self, port=None, device_name=None, milliseconds_on=500,
                       milliseconds_off=2000, connect_on_instantiation=True):
        super().__init__(port, device_name)

        self._on_ms = milliseconds_on
        self._off_ms = milliseconds_off

    def start_stirrer(self):
        """
        Start the stirrer
        """
        self.logger.info(f"{self.identifier} - Starting shaker-stirrer.")

    def stop_stirrer(self):
        """
        Stops the stirrer
        """
        self.logger.info(f"{self.identifier} - Stopping shaker-stirrer.")

    @property
    def milliseconds_on(self):
        return self._on_ms

    @milliseconds_on.setter
    def milliseconds_on(self, on_ms):
        self.logger.info(f"{self.identifier} - On milliseconds set to {on_ms}.")

    @property
    def milliseconds_off(self):
        return self._off_ms

    @milliseconds_off.setter
    def milliseconds_off(self, off_ms):
        self.logger.info(f"{self.identifier} - Off milliseconds set to {off_ms}.")


class SimIKARETControlVisc(SimSerialDevice):
    def __init__(self, port=None, device_name=None):
        super().__init__(port, device_name)

    def start_stirrer(self):
        self.logger.info('IKARET - Starting stirrer')

    def start_heater(self):
        self.logger.info('IKARET - Starting heater')

    def stop_stirrer(self):
        self.logger.info('IKARET - Stopping stirrer')

    def stop_heater(self):
        self.logger.info('IKARET - Stopping heater')

    def temperature_setter(self, temp):
        self.logger.info('IKARET - Temperaure set to: {0}'.format(temp))

    def stir_rate_setter(self, stir_rate):
        self.logger.info('IKARET - Stir rate set to: {0}'.format(stir_rate))


class SimIKARCTDigital(SimSerialDevice):
    def __init__(self, port=None, address=None, name=None, **kwargs):
        super().__init__(port, address, name, **kwargs)

    def start_stirrer(self):
        self.logger.info('IKARCT - Starting stirrer')

    def start_heater(self):
        self.logger.info('IKARCT - Starting heater')

    def stop_stirrer(self):
        self.logger.info('IKARCT - Stopping stirrer')

    def stop_heater(self):
        self.logger.info('IKARCT - Stopping heater')

    def temperature_setter(self, temp):
        self.logger.info('IKARCT - Temperaure set to: {0}'.format(temp))

    def stir_rate_setter(self, stir_rate):
        self.logger.info('IKARCT - Stir rate set to: {0}'.format(stir_rate))


class SimUSBswitch(SimSerialDevice):
    def __init__(self, port=None, device_name=None):
        super().__init__(port, device_name)

    def start_stirrer(self):
        self.logger.info('usbswitch - Starting stirrer')

    def stop_stirrer(self):
        self.logger.info('usbswitch - Stopping stirrer')


class SimIKARV10(SimSerialDevice):
    def __init__(self, port=None, device_name=None):
        super().__init__(port, device_name)

    def initialise(self):
        self.logger.info('IKARV - Initialising')

    def start_heater(self):
        self.logger.info('IKARV - Starting Heater')

    def stop_heater(self):
        self.logger.info('IKARV - Stopping Heater')

    def start_rotation(self):
        self.logger.info('IKARV - Starting Rotations')

    def stop_rotation(self):
        self.logger.info('IKARV - Stopping rotations')

    def lift_up(self):
        self.logger.info('IKARV - Lifting arm')

    def lift_down(self):
        self.logger.info('IKARV - Lifting arm down')

    def reset_rotavap(self):
        self.logger.info('IKARV - Resetting rotavap')

    @property
    def temperature_sp(self):
        self.logger.info('IKARV - Temperature: GIEF TEMP ༼ つ ◕_◕ ༽つ')

    @temperature_sp.setter
    def temperature_sp(self, temp):
        self.logger.info('IKARV - Temperature set to {0}'.format(temp))

    @property
    def rotation_speed_sp(self):
        self.logger.info('IKARV - Speed: GIEF SPEED ༼ つ ◕_◕ ༽つ')

    @rotation_speed_sp.setter
    def rotation_speed_sp(self, speed):
        self.logger.info('IKARV - Speed set to {0}'.format(speed))

    def set_interval_sp(self, interval=None):
        self.logger.info('IKARV - Interval set to {0}'.format(interval))


class SimCVC3000(SimSerialDevice):
    def __init__(self, port=None, address=None, name=None, **kwargs):
        super().__init__(port, address, name, **kwargs)

    def initialise(self):
        self.logger.info("CVC3K - Initialising")

    @property
    def vacuum_sp(self):
        self.logger.info('CVC3K - GIEF SP ༼ つ ◕_◕ ༽つ')

    @vacuum_sp.setter
    def vacuum_sp(self, sp):
        self.logger.info('CVC3k - Set SP to {0}'.format(sp))

    @property
    def speed_sp(self):
        self.logger.info('CVC3K - GIEF SP ༼ つ ◕_◕ ༽つ')

    @speed_sp.setter
    def speed_sp(self, sp):
        self.logger.info('CVC3k - Set SP to {0}'.format(sp))

    def set_mode(self, mode):
        self.logger.info('CVC3K - setting mode to {0}'.format(mode))

    def vacuum_pv(self):
        self.logger.info('CVC3K - Reading vacuum process value.')

    def start(self):
        self.logger.info('CVC3k - Starting vacuum')

    def stop(self):
        self.logger.info('CVC3K - Stopping Vacuum')

    def vent(self):
        self.logger.info('CVC3K - Venting vacuum')

    def query_status(self):
        self.logger.info('CVC3K - Status is ༼ つ ◕_◕ ༽つ')

    @property
    def end_vacuum_sp(self):
        self.logger.info('CVC3K - GIEF END SP ༼ つ ◕_◕ ༽つ')

    @end_vacuum_sp.setter
    def end_vacuum_sp(self, sp):
        self.logger.info('CVC3K - End SP set to {0}'.format(sp))

    @property
    def runtime_sp(self):
        self.logger.info('CVC3K - GIEF RUNTIME SP ༼ つ ◕_◕ ༽つ')

    @runtime_sp.setter
    def runtime_sp(self, sp):
        self.logger.info('CVC3K - Runtime sp set to {0}'.format(sp))


class SimJULABOCF41(SimSerialDevice):
    def __init__(self, port=None, address=None, name=None, **kwargs):
        super().__init__(port, address, name, **kwargs)

    def start(self):
        self.logger.info('Julabo CF41 - Starting operation')

    def stop(self):
        self.logger.info('Julabo CF41 - Stopping operation')

    def set_temperature(self, temp):
        self.logger.info('Julabo CF41 - Temperature sp set to {0}'.format(temp))

    def set_cooling_power(self, cooling_power=100):
        if cooling_power < 0 or cooling_power > 100:
            raise ValueError(
                "ERROR: supplied value {0} is outside the limits (0..100)!".format(
                    cooling_power))
        else:
            self.logger.info(f"Julabo CF41 - Cooling power set to set to {cooling_power}")


class SimHuber(SimSerialDevice):
    def __init__(self, port=None, device_name=None):
        super().__init__(port, device_name)

    def start(self):
        self.logger.info('Huber - Starting operation')

    def stop(self):
        self.logger.info('Huber - Stopping operation')

    def set_temperature(self, temp):
        self.logger.info('Huber - Temperature sp set to {0}'.format(temp))

    def set_ramp_duration(self, ramp_duration):
        self.logger.info(
            'Huber - Ramp duration set to {0}'.format(ramp_duration))

    def start_ramp(self, temp):
        self.logger.info('Huber - Starting ramp to {0}°C'.format(temp))


class SimRZR_2052(SimSerialDevice):
    def __init__(self, port=None, device_name=None):
        super().__init__(port, device_name)

    @property
    def stir_rate_sp(self):
        self.logger.info("RZR 2052 - GIEF SP ༼ つ ◕_◕ ༽つ")

    @stir_rate_sp.setter
    def stir_rate_sp(self, rpm):
        self.logger.info('RZR 2052 - Setting RPM to {0}'.format(rpm))

    def start_stirrer(self):
        self.logger.info('RZR 2052 - Starting operation')

    def stop_stirrer(self):
        self.logger.info('RZR 2052 - Stopping operation')


class SimIKAmicrostar75(SimSerialDevice):
    def __init__(self, port=None, device_name=None):
        super().__init__(port, device_name)

    @property
    def stir_rate_sp(self):
        self.logger.info("IKA microstar - GIEF SP ༼ つ ◕_◕ ༽つ")

    @stir_rate_sp.setter
    def stir_rate_sp(self, rpm):
        self.logger.info('IKA microstar - Setting RPM to {0}'.format(rpm))

    def start_stirrer(self):
        self.logger.info('IKA microstar - Starting operation')

    def stop_stirrer(self):
        self.logger.info('IKA microstar - Stopping operation')

class SimMRHeiConnect(SimSerialDevice):
    def __init__(self, port=None, device_name=None):
        super().__init__(port, device_name)

    def switch_protocol(self, protocol="new"):
        self.logger.info(
            'MRHeiConnect - Switch protocol to {0}'.format(protocol))

    def watchdog_on(self):
        self.logger.info('MRHeiConnect - Turn watchdog on.')

    def query_status(self):
        self.logger.info('MRHeiConnect - Querying status.')

    def start_heating(self):
        self.logger.info('MRHeiConnect - Start heating.')

    @property
    def temperature_sp(self):
        self.logger.info('MRHeiConnect - Get temperature setpoint.')

    @temperature_sp.setter
    def temperature_sp(self, temperature_setpoint):
        self.logger.info(
            'MRHeiConnect - Set temperature setpoint to {0}.'.format(
                temperature_setpoint))

class SimHeiTORQUE_100(SimSerialDevice):
    def __init__(self, port=None, address=None, name=None, **kwargs):
        super().__init__(port, address, name, **kwargs)

    @property
    def stir_rate_sp(self):
        self.logger.info('Hei Torque - getting the rpm value')

    @stir_rate_sp.setter
    def stir_rate_sp(self, rpm):
        self.logger.info(f'Hei Torque - speed set to {rpm}')
    
    def start_stirrer(self):
        self.logger.info('HeiTorque - starting')

    def stop_stirrer(self):
        self.logger.info('HeiTorque - stopping')

class SimTricontC3000(SimSerialDevice):
    def __init__(self, port=None, name=None, **kwargs):
        super().__init__(port, name, **kwargs)

    def init_pump_full(self, valve_enumeration_direction="CW", input_port=None,
                             output_port=None, run=True, address=None):
        self.logger.info('TricontC3000 - Running pump initialisation.')

    def move_plunger_absolute(self, position, set_busy=True, run=True,
                                    address=None):
        self.logger.info(
            'TricontC3000 - Making absolute plunger move to position {0}.'.format(
                position))

    def dispense_relative(self, increments, set_busy=True, run=True,
                                address=None):
        self.logger.info(
            'TricontC3000 - Making relative dispense with increments of {0}.'.format(
                increments))

    def aspirate_relative(self, increments, set_busy=True, run=True,
                                address=None):
        self.logger.info(
            'TricontC3000 - Making relative aspiration with increments of {0}.'.format(
                increments))

    def set_ramp_slope(self, ramp, address=None):
        self.logger.info(
            'TricontC3000 - Setting slope of acceleration/deceleration ramp to {0} for the syringe motor.'.format(
                ramp))

    def set_start_velocity(self, velocity, address=None):
        self.logger.info(
            'TricontC3000 - Setting starting velocity to {0} for the syringe motor.'.format(
                velocity))

    def set_max_velocity(self, velocity, address=None):
        self.logger.info(
            'Setting maximum velocity (top of the ramp) to {0} for the syringe motor.'.format(
                velocity))

    def set_max_velocity_code(self, velocity_code, address=None):
        self.logger.info(
            'Setting maximum velocity (top of the ramp) to {0} for the syringe motor.'.format(
                velocity_code))

    def set_stop_velocity(self, velocity, address=None):
        self.logger.info(
            'Setting stopping velocity to {0} for the syringe motor.'.format(
                velocity))

    def set_resolution_mode(self, resolution_mode, address=None):
        self.logger.info(
            'Setting plunger resolution mode to {0}.'.format(
                resolution_mode))

    def set_valve_type(self, valve_type, address=None):
        self.logger.info('Setting valve type to {0}.'.format(valve_type))

    def set_valve_position(self, position, rotation_direction="CW", address=None):
        self.logger.info('Moving valve to position {0}'.format(position))

    def is_pump_busy(self, address=None):
        self.logger.info('TricontC3000 - Checking if pump is busy.')

    def is_pump_initialized(self, address=None):
        self.logger.info(
            'TricontC3000 - Checking if pump has been successfully initialised.')

    def get_pump_configuration(self, address=None):
        self.logger.info('TricontC3000 - Get pump EEPROM configuration.')

    def get_plunger_position(self, address=None):
        self.logger.info('TricontC3000 - Get absolute plunger position.')

    def get_valve_position(self, address=None):
        self.logger.info('TricontC3000 - Reading current position of valve.')
