# coding=utf-8
# !/usr/bin/env python
# * ========================================================================= */
# *                                                                           */
# *   hotplate_operations.py                                                  */
# *   (c) 2017 Sebastian Steiner, The Cronin Group, University of Glasgow     */
# *                                                                           */
# *   This script controls a stirrer hotplate for the synthesis of            */
# *   Baclofen in plastic reactionware.                                       */
# *                                                                           */
# * ========================================================================= */

# system imports
from time import sleep

# additional module imports
from SerialLabware import IKARETControlVisc

# serial port the stirrer is connected to
com_port = "COM11"

# instantiate the stirrer object
stirrer = IKARETControlVisc(port=com_port, connect_on_instantiation=True)

# main script
sleep(60)
stirrer.stir_rate_sp = 500
stirrer.start_stirrer()

sleep(18180)
stirrer.stop_stirrer()

sleep(60)
stirrer.start_stirrer()

sleep(9360)
stirrer.temperature_sp = 40
stirrer.start_heater()

sleep(7200)
stirrer.stop_heater()

sleep(9360)
stirrer.temperature_sp = 100
stirrer.start_heater()

sleep(86400)
stirrer.temperature_sp = 70

sleep(11700)
stirrer.stop_heater()

sleep(2700)
stirrer.stop_stirrer()
