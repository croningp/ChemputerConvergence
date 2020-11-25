# coding=utf-8
# !/usr/bin/env python
# * ========================================================================= */
# *                                                                           */
# *   multiple_devices.py                                                     */
# *   (c) 2018 Sebastian Steiner, The Cronin Group, University of Glasgow     */
# *                                                                           */
# *   This script controls two stirrer hotplates, a rotary evaporator and a   */
# *   vacuum pump.                                                            */
# *                                                                           */
# * ========================================================================= */

# additional module imports
from SerialLabware import IKARETControlVisc, IKARV10, CVC3000

# serial ports
left_stirrer_port = "COM11"
right_stirrer_port = "COM12"
rotavap_port = "COM13"
vacuum_port = "COM14"

# instantiate all objects
left_stirrer = IKARETControlVisc(port=left_stirrer_port, device_name="left hotplate stirrer", connect_on_instantiation=True)
right_stirrer = IKARETControlVisc(port=right_stirrer_port, device_name="right hotplate stirrer", connect_on_instantiation=True)
rotavap = IKARV10(port=rotavap_port, device_name="rotary evaporator", connect_on_instantiation=True)
vacuum_pump = CVC3000(port=vacuum_port, device_name="vacuum pump", connect_on_instantiation=True)

# initialise rotavap and vacuum pump (not all devices need to be initialised, refer to documentation)
rotavap.initialise()
vacuum_pump.initialise()

# stir left stirrer at 200rpm
left_stirrer.stir_rate_sp = 200  # this is a property. Properties can be set like this.
left_stirrer.start_stirrer()

# heat right stirrer to 100°C
left_stirrer.temperature_sp = 100
left_stirrer.start_heater()

# lower down rotavap arm, start rotation at 100rpm, and set temperature to 40°C
rotavap.lift_down()
rotavap.rotation_speed_sp = 100
rotavap.start_rotation()
rotavap.temperature_sp = 40
rotavap.start_heater()

# set vacuum to 800mbar, start vacuum
vacuum_pump.vacuum_sp = 800
vacuum_pump.start()

# print current temperature of the right hotplate
print(right_stirrer.temperature_pv)

# print current vacuum
print(vacuum_pump.vacuum_pv)

# stop all operations
left_stirrer.stop_stirrer()
right_stirrer.stop_heater()
rotavap.stop_rotation()
rotavap.stop_heater()
vacuum_pump.stop()
