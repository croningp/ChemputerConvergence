# coding=utf-8
# !/usr/bin/env python
"""
"valve_config" -- Initial configuration of Chemputer valves
============================================================

.. module:: valve_config
   :platform: Unix, Windows
   :synopsis: Configure a newly programmed valve and make it ready for use.
.. moduleauthor:: Sebastian Steiner <s.steiner.1@research.gla.ac.uk>

(c) 2018 The Cronin Group, University of Glasgow. This work is licensed under BSD 3-clause.

This example shows how to configure a Chemputer valve after programming it. This process may be done in an automated
fashion by running this script, or by sending the commands one by one from the command line.

For style guide used see http://xkcd.com/1513/
"""

from ChemputerAPI import ChemputerValve

# Unless your script implements a logger of its own, you may want to configure and enable logging to read the API's
# messages and replies. This can also be accomplished by uncommenting this statement in line 54 in the API.
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s ; %(levelname)s ; %(message)s")

# Then, instantiate your device. By default, after programming the device will have the IP ending 99.
valve = ChemputerValve("192.168.1.99")

# The valve requires some pieces of information to function correctly. Thus, the first thing to do is to write a default
# configuration to the device:
valve.write_default_valve_configuration()

# The valve should reply the values, followed by a confirmation that the config write was successful.
# Next, errors are cleared:
valve.clear_errors()

# It is advisable to check if the device is now free of errors:
valve.read_errors()

# Next, the valve needs to count its magnets and determine the home magnet direction. Manually move the valve between
# positions (no matter which positions exactly, just make sure its not precisely centred on one position), then call
# auto_config():
valve.auto_config()

# The valve will turn two full revolutions, and hopefully report success. Common errors here are:
#
# * Six positive and zero negative magnets (or the other way around) are found: during assembly, the home magnet was not
#   put in the other way. Replace the magnet on the position labeled "3" with one pointing the other way.
#
# * Six positive and one negative magnets (or the other way around) are found: the valve was centred on one position
#   prior to calling auto_config(), and this position is counted twice. This happens sometimes. Move the valve between
#   two positions, write the default config again, and run auto_config() once more.
#
# * Fewer than six magnets (in total) are found: Either a magnet is physically missing (check the valve), or one or more
#   magnets are too weak (demagnetisation due to shock or impact, production fault, etc.). Manually move the valve from
#   position to position, and call read_ADC(). "Negative" magnets should read below 1700, "positive" magnets above 2800.
#   If no faulty magnet can be identified, it's likely a problem with the Hall sensor.
#
# * More than six magnets (in total) are found: This is almost always a faulty Hall effect sensor.
#
# * The correct total amount is detected, but more than one is "the other way around": That's pretty clear, someone
#   cocked up the assembly. Use read_ADC(), another magnet, or a magnet polarity indicator to work out the wrong magnets
#   and replace them.

# Once successfully configured, the valve is ready for use. It is recommended to have it make a few moves and check if
# everything works:
valve.move_home()  # First move is ALWAYS to home. Check if homing works as expected.
valve.wait_until_ready()
valve.move_to_position(3)
valve.wait_until_ready()
valve.move_to_position(1)  # check if it moves backwards
valve.wait_until_ready()
valve.move_home()  # check if it returns to the proper home position
valve.wait_until_ready()

# Lastly, a new IP address is assigned:
valve.assign_ip_address("192.168.1.11")

# At this point the script will hang until the TCP connection times out, but it matters not. The configuration is done
# and the device is ready for use.
